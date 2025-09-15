from typing import List, Type
from typing_extensions import TypedDict

from pydantic import BaseModel, Field

from pipeline.dependencies.models.wire_models import (DynamicAtonData,
                                                      DynamicSARData,
                                                      DynamicVesselData,
                                                      DynamicVoyage, WireData)


class MessageTypeEntry(BaseModel):
    message_type: str
    model: Type[DynamicVesselData | DynamicSARData | DynamicAtonData | DynamicVoyage]
    table: str
    


unvalidated_message_type_map: List[dict] = [
    {"message_type": "0", "model": DynamicVesselData, "table": "dynamic_vessel"},
    {"message_type": "1", "model": DynamicSARData, "table": "dynamic_sar"},
    {"message_type": "2", "model": DynamicAtonData, "table": "dynamic_aton"},
    {"message_type": "3", "model": DynamicVoyage, "table": "dynamic_voyage"},
]


def get_message_type_map() -> list[MessageTypeEntry]:
    valid_models = [MessageTypeEntry(**model) for model in unvalidated_message_type_map]
    return valid_models

class MessageTypeMap(BaseModel):
    """
    this files consist of message fan out mapping for the data_writer

    message_type_map contains mapping of which message type (received in the wire/kafka or in local testing from json)
    will be inserted to which table and what its associated Pydantic model to handle validation

    if more tables are needed to be inserted they should be added to the message_type_map
    
    This mapping serves as global map for the messages traveling in the wire that are insterted to the table
    trough this service. 
    
    If other message types are to be come trough this service the Models should be mapped out here to their
    correct tables
    

    """

    types: list[MessageTypeEntry] = Field(default_factory=get_message_type_map)

    def get_message_keys(self) -> list[str]:
        return [m_type.message_type for m_type in self.types]

    def get_message_topics(self) -> list[str]:
        return [m_type.table for m_type in self.types]

    def get_message_tables(self) -> list[str]:
        return [m_type.table for m_type in self.types]

    def get_message_key_by_table(self, table: str) -> str:
        keys = [m_type.message_type for m_type in self.types if m_type.table == table]
        return next(iter(keys))

    def get_table_by_key(self, key: str) -> str:
        tables = [m_type.table for m_type in self.types if key == m_type.message_type]
        return next(iter(tables))

    def get_model_by_message_type(self, message_type: str) -> type[WireData]:
        models = [
            m_type.model for m_type in self.types if message_type == m_type.message_type
        ]
        return next(iter(models))

