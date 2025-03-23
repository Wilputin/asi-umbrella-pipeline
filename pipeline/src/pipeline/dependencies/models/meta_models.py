import pandas as pd
from pydantic import BaseModel, ConfigDict


class BaseMetaData(BaseModel):
    """
    For now this would be empty but can be a centralized way to control attribute formatting to the db
    when data models inherit this pydantic model
    """


class ShipTypes(BaseMetaData):
    """
    example/
    id_shiptype,shiptype_min,shiptype_max,type_name,ais_type_summary
    1,10,19,Reserved,Unspecified

    """

    id_shiptype: int
    shiptype_min: int
    shiptype_max: int
    type_name: str
    ais_type_summary: str

    @staticmethod
    def convert_df_to_tuple(data: pd.DataFrame) -> list[tuple]:
        validated_rows = []
        for row in data.itertuples(index=False, name=None):
            datamodel = ShipTypes(
                id_shiptype=row[0],
                shiptype_min=row[1],
                shiptype_max=row[2],
                type_name=row[3],
                ais_type_summary=row[4],
            )
            validated_rows.append(
                (
                    datamodel.id_shiptype,
                    datamodel.shiptype_min,
                    datamodel.shiptype_max,
                    datamodel.type_name,
                    datamodel.ais_type_summary,
                )
            )
        return validated_rows


class ShipTypeDetailed(BaseMetaData):
    """
    example/
    id_detailedtype,detailed_type,id_shiptype
    1,Wing In Ground Effect Vessel,2
    """

    id_detailedtype: int
    detailed_type: str
    id_shiptype: int

    @staticmethod
    def convert_df_to_tuple(data: pd.DataFrame) -> list[tuple]:
        validated_rows = []
        for row in data.itertuples(index=False, name=None):
            datamodel = ShipTypeDetailed(
                id_detailedtype=row[0], detailed_type=row[1], id_shiptype=row[2]
            )
            validated_rows.append(
                (
                    datamodel.id_detailedtype,
                    datamodel.detailed_type,
                    datamodel.id_shiptype,
                )
            )
        return validated_rows


class NavigationalStatus(BaseMetaData):
    status: int
    description: str

    @staticmethod
    def convert_df_to_tuple(data: pd.DataFrame) -> list[tuple]:
        validated_rows = []
        for row in data.itertuples(index=False, name=None):
            datamodel = NavigationalStatus(status=row[0], description=row[1])
            validated_rows.append((datamodel.status, datamodel.description))
        return validated_rows


class MMSICode(BaseMetaData):
    mmsi_prefix: int
    country: str

    @staticmethod
    def convert_df_to_tuple(data: pd.DataFrame) -> list[tuple]:
        validated_rows = []
        for row in data.itertuples(index=False, name=None):
            aton_model = MMSICode(mmsi_prefix=row[0], country=row[1])
            validated_rows.append((aton_model.mmsi_prefix, aton_model.country))
        return validated_rows


class AtonTypes(BaseMetaData):
    """
    defined based on source data
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    nature: str | None
    code: int
    definition: str

    @staticmethod
    def convert_df_to_tuple(data: pd.DataFrame) -> list[tuple]:
        validated_rows = []
        for row in data.itertuples(index=False, name=None):
            aton_model = AtonTypes(code=row[1], nature=row[0], definition=row[2])
            validated_rows.append(
                (aton_model.code, aton_model.nature, aton_model.definition)
            )
        return validated_rows
