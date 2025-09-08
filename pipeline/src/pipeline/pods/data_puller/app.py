import asyncio
import concurrent
import concurrent.futures
import functools
import json
import pathlib
import time
from uuid import uuid4

import pandas as pd
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from pydantic import BaseModel, ConfigDict
from pipeline.dependencies.data_process import static_functions
from pipeline.dependencies.base_app.base_app import BaseApp
from pipeline.dependencies.decoder.message_map import (MessageTypeMap,
                                                       get_message_type_map)
from pipeline.dependencies.driver.db_driver import DbDriver


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    messages: list[tuple] = []
    db_driver: DbDriver


class DataPuller(BaseApp):
    loop: asyncio.AbstractEventLoop
    tpe: concurrent.futures.ThreadPoolExecutor
    producer: Producer | None = None
    root_repo_dir = pathlib.Path(__file__).parents[4]
    data_source: pathlib.Path = root_repo_dir / "./data"
    admin: AdminClient | None = None
    message_map: MessageTypeMap
    data_size_protection: int = 1000
    data_samples: dict[str, pd.DataFrame] #small datasample to keep in state that we regenerate constantly
    produced_data: float = 0.0

    async def on_init(self) -> None:
        self.live = True
        self.message_map = MessageTypeMap()
        self.loop = asyncio.get_running_loop()
        self.tpe = concurrent.futures.ThreadPoolExecutor()
        self.data_samples = dict()
        self.data_sample_size = dict()
        if self.connection_config.use_kafka:
            await self.setup_kafka()
        for message_map in self.message_map.types:
            message_table = message_map.table
            df = await self.processing_pipeline(data=message_table)
            size_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
            if size_mb > self.data_size_protection:
                msg = "Dataframe size is over 1gB. Ingest smaller dataset for cost effectiviness"
                raise ValueError(msg)
            self.logger.info("dataframe size for %s is %d mB", message_map.table, size_mb)
            self.data_samples[message_map.table] = df
            self.data_sample_size[message_table] = size_mb

    async def run_live_app(self):
        tasks = list()
        for message_table, df in self.data_samples.items():
            await self.produce_df_to_topic(df=df, data=message_table)
            self.produced_data += self.data_sample_size[message_table]

    async def create_topic(self, topic: str) -> None:
        self.logger.info(
            "creating topic %s and my kafka address is %s",
            topic,
            self.get_kafka_address(),
        )
        if self.admin is None:
            raise ValueError("kafka admin is not set")
        topics = [NewTopic(topic, num_partitions=3, replication_factor=1)]
        partial = functools.partial(self.admin.create_topics, topics)
        await self._partial_run(partial)

    async def setup_kafka(self) -> None:
        self.admin = AdminClient(
            {"bootstrap.servers": self.get_kafka_address()}  # <-- string, not list
        )

        conf = {
            "bootstrap.servers": self.get_kafka_address(),
            "client.id": f"csv-to-kafka-producer-{uuid4()}",
            "batch.num.messages": 1000,
            "queue.buffering.max.kbytes": (1048576) * 2,  # 2gb buffer
        }

        self.producer = Producer(conf)
        for topic in self.message_map.get_message_topics():
            await self.create_topic(topic)

    async def convert_nan(self, data: dict, target=None) -> dict:
        for key, value in data.items():
            if pd.isna(value):
                data[key] = target
        return data

    async def produce_df_to_topic(self, df: pd.DataFrame, data: str) -> None:
        if self.producer is None:
            return
        self.logger.debug(f"starting data dump to topic {data}")
        index = 0
        total_size = len(df)
        flush_interval = int(len(df) * 0.3)  # should be coming from the configs
        poll_interval = int(len(df) * 0.01)
        poll_index = 0
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict = await self.convert_nan(data=row_dict)
            json_value = json.dumps(row_dict)
            kwargs = dict(topic=data, value=json_value.encode("utf-8"))
            try:
                self.producer.produce(**kwargs)
            except BufferError as e:
                msg = (
                    "buffer error: {} and as result decreasing polling interval".format(
                        e
                    )
                )
                self.logger.warning(msg)
                poll_interval = int(poll_interval * 0.5)
                poll_index = poll_interval
            if poll_index >= poll_interval:
                self.producer.poll(0)
                poll_index = 0
            if self.connection_config.message_size:
                processed = int(idx) / total_size
                if processed >= self.connection_config.message_size:
                    self.logger.info(
                        f"message size exceeded exiting the data dumping task for data {data}"
                    )
                    break
            if int(idx) % flush_interval == 0:
                self.logger.info(
                    "flushing the producer after interval of %s messages",
                    flush_interval,
                )
                await self._partial_run(functools.partial(self.producer.flush, 5))
            index += 1
            poll_index += 1
        self.producer.flush()

    async def processing_pipeline(self, data: str) -> pd.DataFrame:
        filepath = self.data_source / f"{data}.parquet"
        self.logger.info("trying to read csv from filepath %s", filepath)
        df = pd.read_parquet(filepath, engine="pyarrow")
        processed_df = self._process_df(df=df, data=data)
        return processed_df


    def _process_df(self, df: pd.DataFrame, data: str) -> pd.DataFrame:
        if "ts" in df.columns:
            df.rename(columns={"ts": "t"}, inplace=True)
        df.sort_values(by="t", inplace=True, ascending=True)
        processed_df = static_functions.divide_mmsi_and_country_code(df)
        message_type = self.message_map.get_message_key_by_table(data)
        processed_df["message_type"] = [message_type for _ in range(len(processed_df))]
        processed_df.reset_index(inplace=True, drop=True)
        return processed_df


    async def _partial_run(self, partial: functools.partial):
        return await self.loop.run_in_executor(executor=self.tpe, func=partial)
