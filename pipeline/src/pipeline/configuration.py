from pydantic import BaseModel, Field


class ConnectionConfig(BaseModel):
    """
    handles connection configuration if we are testing in localhost or running compose network
    """

    localhost: bool = False
    compose: bool = True
    use_kafka: bool = (
        True  # if False for local testing csv are transformed to json objects to folder src/kafka_data/
    )
    message_size: float | None = None # only relevant for kafka


class MetaConfig(BaseModel):
    table: str
    delimiter: str
    headers: bool


class Configuration(BaseModel):
    connection_config: ConnectionConfig = Field(default_factory=ConnectionConfig)
    meta_config: list[MetaConfig] | None = None
    log_level: str = "info"



class ModuleConfig(BaseModel):
    active: bool = True
    config: Configuration = Field(default_factory=Configuration)
    name: str



class PipelineConfiguration(BaseModel):
    modules: list[ModuleConfig]

