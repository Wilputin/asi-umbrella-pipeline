import datetime
import typing
from abc import abstractmethod
from typing import cast

from pydantic import BaseModel, model_validator


class WireData(BaseModel):
    """
    type is specified in the base model and it should be joined to the raw message
    by the data-puller

    In the future ETL pipeline datamodels should be centralized in single image
    that services can pull as dependency


    All datamodels that are traveling in the wire should inherit from this class
    so we assert that we always no its origin

    if we expect any other data to be traveling in the wire they should be added in this file

    """

    message_type: str

    @abstractmethod
    def get_tuple_for_insertion(self) -> tuple: ...


class DynamicCommonData(WireData):
    """
    this class represents common data points for the vessel, sar and aton data

    """

    country_code: int
    sourcemmsi: int
    t: (
        int | datetime.datetime
    )  # data is ts and t for sar and vessel. pipeline should handle key transformation

    @model_validator(mode="after")
    def transform_datetime(self) -> typing.Self:
        epoch = self.t
        timestamp = datetime.datetime.fromtimestamp(cast(float, epoch))
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        self.t = timestamp
        return self


class DynamicCommonVesselData(DynamicCommonData):
    """
    this class represents common data points for the vessel and Sar data

    """

    speedoverground: float
    courseoverground: float
    lon: float
    lat: float


class DynamicVesselData(DynamicCommonVesselData):
    """
    this class introduces unique datapoints for the vessel data
    """

    navigationalstatus: int | None
    rateofturn: float | None
    trueheading: float | None

    def get_tuple_for_insertion(self):
        attributes = [
            "t",
            "sourcemmsi",
            "navigationalstatus",
            "rateofturn",
            "speedoverground",
            "courseoverground",
            "trueheading",
            "lon",
            "lat",
            "country_code",
        ]
        model_dump = self.model_dump()
        tuple_model = tuple(model_dump[f] for f in attributes)
        return tuple_model


class DynamicSARData(DynamicCommonVesselData):
    """
    this class introduces unique datapoints for the Sar data
    """

    altitude: float

    def get_tuple_for_insertion(self):
        attributes = [
            "t",
            "sourcemmsi",
            "altitude",
            "speedoverground",
            "courseoverground",
            "lon",
            "lat",
            "country_code",
        ]
        model_dump = self.model_dump()
        tuple_model = tuple(model_dump[f] for f in attributes)
        return tuple_model


class DynamicAtonData(DynamicCommonData):
    """
    this class introduces unique datapoints for the Aton data
    """

    typeofaid: int
    aidsname: str
    virtual: str
    lon: float
    lat: float

    def get_tuple_for_insertion(self):
        attributes = [
            "t",
            "sourcemmsi",
            "typeofaid",
            "aidsname",
            "virtual",
            "lon",
            "lat",
            "country_code",
        ]

        model_dump = self.model_dump()
        tuple_model = tuple(model_dump[f] for f in attributes)
        return tuple_model


class DynamicVoyage(DynamicCommonData):
    callsign: str | None
    imonumber: int | None
    shipname: str | None
    shiptype: int | None
    tobow: int | None
    tostern: int | None
    tostarboard: int | None
    toport: int | None
    eta: str | None
    draught: float | None
    destination: str | None
    mothershipmmsi: int | None

    def get_tuple_for_insertion(self):
        attributes = [
            "t",
            "sourcemmsi",
            "country_code",
            "imonumber",
            "callsign",
            "shipname",
            "shiptype",
            "tobow",
            "tostern",
            "tostarboard",
            "toport",
            "eta",
            "draught",
            "destination",
            "mothershipmmsi",
        ]
        model_dump = self.model_dump()
        tuple_model = tuple(model_dump[f] for f in attributes)
        return tuple_model
