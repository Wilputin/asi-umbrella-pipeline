import asyncio
import concurrent
import concurrent.futures
import functools
import json
import pathlib

from confluent_kafka import Consumer, Message
from confluent_kafka.admin import AdminClient
from pydantic import BaseModel, ConfigDict

from pipeline.dependencies.base_app.base_app import BaseApp
from pipeline.dependencies.decoder.message_decoder import MessageDecoder
from pipeline.dependencies.decoder.message_map import (MessageTypeMap,
                                                       get_message_type_map)
from pipeline.dependencies.driver.db_driver import DbDriver


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    messages: list[tuple] = []
    db_driver: DbDriver


class DataWriter(BaseApp):
    loop: asyncio.AbstractEventLoop
    tpe: concurrent.futures.ThreadPoolExecutor
    admin: AdminClient
    message_queues: dict[str, asyncio.Queue]
    consumers: dict[str, Consumer] | None = None
    root_repo_dir = pathlib.Path(__file__).parents[4]
    data_source: pathlib.Path = root_repo_dir / "./kafka_data"
    message_map: MessageTypeMap

    async def on_init(self) -> None:
        self.state = AppState(
            db_driver=DbDriver(
                logger=self.logger, connection_config=self.connection_config
            )
        )
        self.message_map = MessageTypeMap()
        self.message_queues = {
            key: asyncio.Queue() for key in self.message_map.get_message_keys()
        }
        if self.connection_config.use_kafka:
            self.consumers = await self.gather_consumers(
                topics=self.message_map.get_message_topics(),
                service_name=self.logger.name,
            )
        self.loop = asyncio.get_running_loop()
        self.tpe = concurrent.futures.ThreadPoolExecutor()
        self.decoder = MessageDecoder(expect_kafka_message=True,
            logger=self.logger
        )
    async def run(self):
        tasks = []
        for message_mapping in self.message_map.types:
            message_table = message_mapping.table
            message_key = message_mapping.message_type
            gathering_task = self.gather_data_from_topic(topic=message_table)
            db_task = self.db_write_loop(message_key)
            tasks.append(asyncio.create_task(gathering_task))
            tasks.append(asyncio.create_task(db_task))
        for task in tasks:
            task.add_done_callback(self.log_task_error)
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.state.db_driver.pool.close()
        await self.close_consumers()

    async def close_consumers(self):
        self.logger.info("closing all consumers")
        for consumer in self.consumers.values():
            consumer.close()

    async def gather_data_from_topic(self, topic: str) -> None:
        if self.consumers is None:
            return
        consumer = self.consumers[topic]
        self.logger.info(f"starting task to gather data from topic {topic}")
        max_trials = 10
        received_messages = False
        while max_trials > 0:
            key = self.message_map.get_message_key_by_table(topic)
            messages = await self.aconsume(consumer)
            if messages:
                received_messages = True
                async for decoded_msg in self.decoder.decode_messages(
                    messages=messages
                ):
                    await self.message_queues[key].put(decoded_msg)
            else:
                await asyncio.sleep(0.5)
                max_trials -= 1
        if not received_messages:
            self.logger.warning(
                f"havent received a single message...Exiting from task for data {topic}"
            )
        else:
            self.logger.info(
                f"havent received new messages in a while...Exiting from task for data {topic}"
            )

    async def gather_data_from_folder(self, topic: str) -> None:
        file_name = f"{topic}.json"
        filepath = self.data_source / file_name

        message_key = self.message_map.get_message_key_by_table(topic)
        data = self.load_json_objects(filepath)
        self.logger.info(f"starting to decode messsages from file {file_name}")
        async for decoded_msg in self.decoder.decode_messages(
            messages=data, use_kafka=False
        ):
            await self.message_queues[message_key].put(decoded_msg)
        self.logger.info(f"gathered data from file {file_name}")

    def load_json_objects(self, file_path: pathlib.Path) -> list[dict]:
        with open(file_path, "r") as f:
            json_array = json.load(f)
            return json_array

    async def batch_messages(
        self, key: str, timeout: float = 1, batch_size: int = 5000
    ):
        messages: list[tuple] = []
        try:
            await asyncio.sleep(1)
            start_time = asyncio.get_event_loop().time()
            while len(messages) < batch_size:
                remaining = timeout - (asyncio.get_event_loop().time() - start_time)
                if remaining <= 0:
                    break
                try:
                    msg = await asyncio.wait_for(
                        self.message_queues[key].get(), timeout=remaining
                    )
                    messages.append(msg)
                except asyncio.TimeoutError:
                    break
        except asyncio.TimeoutError:
            pass
        return messages

    async def db_write_loop(self, key: str) -> None:
        table_name = self.message_map.get_table_by_key(key)
        self.logger.info(
            f"starting task to write data for message type {key} for table {table_name}"
        )
        self.running = True
        max_trials = 20  # we will wait N number of iterations before killing the task. For proper usage this should be done more gracefully
        while max_trials > 0:
            messages = await self.batch_messages(key=key, batch_size=10000)
            table_name = self.message_map.get_table_by_key(key)
            if messages:
                await self.state.db_driver.insert_streaming_data(
                    data=messages, table_name=table_name, batch_size=10000
                )
            else:
                await asyncio.sleep(0.5)
                max_trials -= 1
                self.logger.info(
                    f"message queue is empty on message key {key} sleeping on task for 1 sec..."
                )
                await asyncio.sleep(1)
        self.logger.info(
            f"ending task to write data for message type {key} for table {table_name}"
        )

    async def aconsume(
        self, consumer: Consumer, num_messages: int = 10000
    ) -> list[Message]:
        kwargs = {
            "num_messages": num_messages,
            "timeout": 2,
        }
        partial = functools.partial(consumer.consume, **kwargs)
        messages = await self._partial_run(partial)
        return messages

    async def _partial_run(self, partial: functools.partial):
        return await self.loop.run_in_executor(executor=self.tpe, func=partial)
