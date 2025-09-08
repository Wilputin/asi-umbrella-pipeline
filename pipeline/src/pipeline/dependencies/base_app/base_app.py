import logging
import sys
import time
import traceback
from abc import abstractmethod
from uuid import uuid4

from confluent_kafka import Consumer

from pipeline.configuration import Configuration, ConnectionConfig, MetaConfig

COLOR_CODES = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset to default
}

APPLICATION_COLOR_CODES = {
    "meta_ingestion": "\033[95m",  # Magenta
    "data_puller": "\033[94m",     # Blue
    "data_writer": "\033[91m",     # Green
}

log_format = "[pod:%(name)s]-[time:%(asctime)s]-[level:%(levelname)s]//:%(message)s"
date_format = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLOR_CODES.get(record.levelname, COLOR_CODES["RESET"])
        reset = COLOR_CODES["RESET"]
        record.levelname = f"{log_color}{record.levelname}{reset}"
        log_color = APPLICATION_COLOR_CODES.get(record.name, COLOR_CODES["RESET"])
        record.name = f"{log_color}{record.name}{reset}"
        return super().format(record)


class BaseApp:
    logger: logging.Logger
    running: bool = False
    live: bool = False
    exit_after: int = 10
    connection_config: ConnectionConfig
    meta_config: list[MetaConfig] | None
    produced_data: int = 0

    def __init__(self, logger: logging.Logger, config: Configuration):
        std_handler = logging.StreamHandler(sys.stdout)
        std_handler.setLevel(level=logging.DEBUG)
        logger.info("package started with record name %s", logger.name)
        formatter = ColoredFormatter(log_format, date_format)
        std_handler.setFormatter(formatter)
        logger.addHandler(std_handler)
        self.connection_config = config.connection_config
        self.meta_config = config.meta_config
        self.logger = logger
        self.logger.info(f"starting pod: {logger.name}")
        self.logger.info(f" your connection configuration is {config.model_dump()}")


    @abstractmethod
    async def run_live_app(self):
        raise NotImplementedError
    @abstractmethod
    async def run(self):
        raise NotImplementedError

    @abstractmethod
    def on_init(self):
        raise NotImplementedError

    async def main(self):
        await self.on_init()
        if self.live:
            start_time = time.perf_counter()
            self.logger.info("starting the live app simulation...")
            elapsed_time = 0
            self.running = True
            while self.exit_after > elapsed_time and self.running:
                await self.run_live_app()
                elapsed_time = time.perf_counter() - start_time
                if elapsed_time > self.exit_after:
                    self.running = False
            self.logger.info("application produced %d mB amount of data in %d seconds", self.produced_data,elapsed_time)
            self.logger.info("Troughput is approx %d : mB/s",(round(self.produced_data / elapsed_time)))

        else:
            await self.run()
        package_name = self.logger.name
        self.logger.info(f"pod: {package_name} finished succesfully...")

    def get_kafka_address(self) -> str:
        if self.connection_config.localhost:
            return "localhost:9092"
        if self.connection_config.compose:
            return "kafka:29092"
        raise Exception("No Kafka address configured")

    async def gather_consumers(
        self, topics: list[str], service_name: str
    ) -> dict[str, Consumer]:
        consumer_conf = {
            "bootstrap.servers": self.get_kafka_address(),
            "group.id": f"{service_name}-{uuid4()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
            "security.protocol": "PLAINTEXT",
        }
        self.logger.info("im starting a consumer with configuration:", consumer_conf)
        consumers = dict()
        for topic in topics:
            consumer = Consumer(consumer_conf)
            consumer.subscribe([topic])
            consumers[topic] = consumer
        return consumers

    def log_task_error(self, task):
        try:
            task.result()
        except Exception as e:
            print("Task error:")
            traceback.print_exception(type(e), e, e.__traceback__)
