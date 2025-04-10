import pathlib

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pipeline.dependencies.base_app.base_app import BaseApp
from pipeline.dependencies.driver.db_driver import DbDriver
from pipeline.dependencies.models import meta_models


class MetaData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    values: pd.DataFrame | None = None
    ship_types: bool = False
    ship_types_detailed: bool = False
    mmsi_codes: bool = False
    navigational_status: bool = False
    aton: bool = False

    def set_file_to_true(self, filename: str) -> None:
        if hasattr(self, filename):
            setattr(self, filename, True)


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data: list[MetaData] = []
    db_driver: DbDriver


class MetaIngestion(BaseApp):
    state: AppState
    root_repo_dir = pathlib.Path(__file__).parents[4]
    metadata_source: pathlib.Path = root_repo_dir / "./metadata"
    metadata_files: list[str] = [
        "aton",
        "mmsi_codes",
        "navigational_status",
        "ship_types",
        "ship_types_detailed",
    ]
    meta_delimiters: dict[str, str]

    async def on_init(self):
        db_driver = DbDriver(
            logger=self.logger, connection_config=self.connection_config
        )
        self.state = AppState(db_driver=db_driver)
        self.ingest_metadata()

    async def run(self) -> None:
        for data in self.state.data:
            if data.aton:
                validated_data = meta_models.AtonTypes.convert_df_to_tuple(data.values)
                await self.state.db_driver.insert_meta(
                    data=validated_data, table_name="aton_type"
                )
            if data.mmsi_codes:
                validated_data = meta_models.MMSICode.convert_df_to_tuple(data.values)
                await self.state.db_driver.insert_meta(
                    data=validated_data, table_name="mmsi_codes"
                )
            if data.navigational_status:
                validated_data = meta_models.NavigationalStatus.convert_df_to_tuple(
                    data.values
                )
                await self.state.db_driver.insert_meta(
                    data=validated_data, table_name="navigational_status"
                )
            if data.ship_types:
                validated_data = meta_models.ShipTypes.convert_df_to_tuple(data.values)
                await self.state.db_driver.insert_meta(
                    data=validated_data, table_name="ship_types"
                )
            if data.ship_types_detailed:
                validated_data = meta_models.ShipTypeDetailed.convert_df_to_tuple(
                    data.values
                )
                await self.state.db_driver.insert_meta(
                    data=validated_data, table_name="ship_types_detailed"
                )
        await self.state.db_driver.pool.close()

    def get_delimiter_by_table(self, table: str) -> str:
        if self.meta_config is None:
            raise ValueError("Meta configuration is empty")
        for config in self.meta_config:
            if config.table == table:
                return config.delimiter
        raise ValueError("couldnt find a delimiter")

    def get_headers_by_table(self, table: str) -> bool:
        if self.meta_config is None:
            raise ValueError("Meta configuration is empty")
        for config in self.meta_config:
            if config.table == table:
                return config.headers
        raise ValueError("couldnt find a table")

    def ingest_metadata(self):
        # optimal could be csv from external storage system that would be retrieved.
        # Azure blob storage for example
        file_type = ".csv"
        for config in self.meta_config:
            metadata = MetaData()
            filepath = self.metadata_source / f"{config.table}{file_type}"
            self.logger.info(f"ingesting meta from source: {filepath}")
            delimiter = self.get_delimiter_by_table(config.table)
            headers = self.get_headers_by_table(config.table)
            headers = "infer" if headers else None
            df = pd.read_csv(filepath, delimiter=delimiter, header=headers)
            df = df.map(lambda x: None if pd.isna(x) else x)
            metadata.values = df
            metadata.set_file_to_true(config.table)
            self.state.data.append(metadata)
