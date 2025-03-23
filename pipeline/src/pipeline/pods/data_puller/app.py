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

from pipeline.dependencies.base_app.base_app import BaseApp
from pipeline.dependencies.decoder.message_map import (MessageTypeMap,
                                                       get_message_type_map)
from pipeline.dependencies.driver.db_driver import DbDriver

class MetaData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    values: pd.DataFrame | None = None
    ship_types: bool = False
    mmsi_codes: bool = False
    navigational_status: bool = False
    aton: bool = False

    def set_file_to_true(self, filename: str) -> None:
        if hasattr(self, filename):
            setattr(self, filename, True)


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
    data_destination: pathlib.Path = root_repo_dir / "./kafka_data"
    admin: AdminClient | None = None
    message_map: MessageTypeMap

    async def on_init(self) -> None:
        self.message_map = get_message_type_map()
        self.loop = asyncio.get_running_loop()
        self.tpe = concurrent.futures.ThreadPoolExecutor()
        if self.connection_config.use_kafka:
            await self.setup_kafka()

    async def run(self):
        start_time = time.perf_counter()
        tasks = []
        for message_mapping in self.message_map.types:
            message_table = message_mapping.table
            gathering_task = asyncio.create_task(self.process_data(data=message_table))
            tasks.append(gathering_task)
        for task in tasks:
            task.add_done_callback(self.log_task_error)
        await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        self.logger.info(
            f"Data dump completed in {elapsed_time:.2f} seconds "
            f"when kafka connection was {self.connection_config.use_kafka}"
        )

    async def create_topic(self, topic: str) -> None:
        self.logger.info("creating topic %s and my kafka address is %s", topic, self.get_kafka_address())
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
            "queue.buffering.max.kbytes": (1048576)*2,  # 2gb buffer
        }

        self.producer = Producer(conf)
        for topic in self.message_map.get_message_topics():
            await self.create_topic(topic)

    async def process_data(self, data: str) -> None:
        df = await self.processing_pipeline(data=data)
        if self.connection_config.use_kafka:
            await self.produce_df_to_topic(df=df, data=data)
        else:
            await self.produce_df_to_folder(df=df, data=data)

    async def produce_df_to_folder(self, df: pd.DataFrame, data: str) -> None:
        filename = f"{data}.json"
        if not self.data_destination.exists():
            self.logger.info(" creating directory for data dump....")
            self.data_destination.mkdir(parents=True, exist_ok=True)
        filepath = self.data_destination / filename
        self.logger.info(f"starting data dump to file {filename}")
        if filepath.exists():
            self.logger.info(" file already exists in the directory. Skipping...")
            return
        json_values = []

        df = df.head(int(len(df) * 0.01))  # use only 1 % of data for local testing
        total_length = len(df)
        status = int(total_length / 10)
        self.logger.info(f"logging process between {status} rows")
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict = await self.convert_nan(data=row_dict)
            json_values.append(row_dict)
            if idx % status == 0:
                progress_bar = round(int(idx) / len(df) * 100, 1)
                self.logger.info(f"processed {progress_bar}%")
        with open(filepath, "w") as f:
            json.dump(json_values, f, indent=4)
        self.logger.info(f"ending data dump for {data}")
    async def convert_nan(self,data:dict, target=None) -> dict:
        for key, value in data.items():
            if pd.isna(value):
                data[key] = target
        return data
    async def produce_df_to_topic(self, df: pd.DataFrame, data: str) -> None:
        if self.producer is None:
            return
        self.logger.info(f"starting data dump to topic {data}")
        if self.connection_config.message_size:
            self.logger.info(f"task is capping messages to maximum of {self.connection_config.message_size*100}% of the maximum")
        index = 0
        total_size = len(df)
        flush_interval = int(len(df)*0.3)
        poll_interval = int(len(df)*0.01)
        poll_index = 0
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_dict = await self.convert_nan(data=row_dict)
            json_value = json.dumps(row_dict)
            kwargs = dict(topic=data, value=json_value.encode("utf-8"))
            try:
                self.producer.produce(**kwargs)
            except BufferError as e:
                msg = "buffer error: {} and as result decreasing polling interval".format(e)
                self.logger.warning(msg)
                poll_interval = int(poll_interval * 0.5)
                poll_index = poll_interval
            if poll_index >= poll_interval:
                self.producer.poll(0)
                poll_index = 0
            if self.connection_config.message_size:
                processed = int(idx) / total_size
                if processed >= self.connection_config.message_size:
                    self.logger.info(f"message size exceeded exiting the data dumping task for data {data}")
                    break
            if int(idx) % flush_interval == 0:
                self.logger.info("flushing the producer after interval of %s messages", flush_interval)
                await self._partial_run(functools.partial(self.producer.flush, 5))
            index += 1
            poll_index += 1
        self.logger.info(f"ending data dump for {data}")
        self.logger.info("flushin producer before exiting ")
        self.producer.flush()

    async def processing_pipeline(self, data: str) -> pd.DataFrame:
        filepath = self.data_source / f"{data}.csv"
        self.logger.info("trying to read csv from filepath %s", filepath)
        df = pd.read_csv(filepath, low_memory=False)
        if "ts" in df.columns:
            df.rename(columns={"ts": "t"}, inplace=True)
        df.sort_values(by="t", inplace=True, ascending=True)
        processed_df = self.divide_mmsi_and_country_code(df)
        message_type = self.message_map.get_message_key_by_table(data)
        processed_df["message_type"] = [message_type for _ in range(len(processed_df))]
        processed_df.reset_index(inplace=True, drop=True)
        return processed_df

    def divide_mmsi_and_country_code(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        divide mmsi and country code into separate fields
        """
        mmsi_codes = df["sourcemmsi"].tolist()
        raw_mmsi_codes = []
        country_codes = []

        for code in mmsi_codes:

            str_mmsi_code = str(code)
            country_code = int(str_mmsi_code[:3])
            try:
                mmsi_code = int(str_mmsi_code[3:])
            except Exception as e:
                mmsi_code = int(float(str_mmsi_code[3:]))
                self.logger.debug(f"expection passed {e}")
            raw_mmsi_codes.append(mmsi_code)
            country_codes.append(country_code)
        df["sourcemmsi"] = raw_mmsi_codes
        df["country_code"] = country_codes
        return df

    async def _partial_run(self, partial: functools.partial):
        return await self.loop.run_in_executor(executor=self.tpe, func=partial)
