import logging
import os
import unittest

from pipeline.configuration import Configuration
from pipeline.dependencies.driver.query_builder import SQLQueryBuilder
from pipeline.pods.data_writer.app import DataWriter


class TestCase(unittest.IsolatedAsyncioTestCase):


    async def test_case(self):
        """
        db is expected to have data and container running for this to work
        """
        package_name = "test-case"
        connection_config = Configuration()
        if not os.getenv("RUNTIME"):
            connection_config.connection_config.localhost = True
            connection_config.connection_config.compose = False
            connection_config.connection_config.use_kafka = False
        logger = logging.Logger(name=package_name)
        app = DataWriter(logger=logger, config=connection_config)
        await app.on_init()

        qb = SQLQueryBuilder("vessel")
        results = (qb
                   .where("speedoverground > %s", (0.05,))
                   .order_by("timestamp DESC")
                   .limit(10)
                   .build_query())
        query = results[0]
        params = results[1]
        await app.state.db_driver.query_data(query=query,params=params)

        qb = SQLQueryBuilder("vessel")
        results = (qb
                    .join("INNER", "voyage", "dynamic_vessel.mmsi = dynamic_voyage.mmsi")
                    .select(["dynamic_vessel.lat", "dynamic_vessel.lon"])
                    .where("dynamic_vessel.country_code = %s", (228,))
                   .order_by("dynamic_vessel.timestamp DESC")
                   .limit(10)
                   .build_query())
        query = results[0]
        params = results[1]
        results = await app.state.db_driver.query_data(query=query, params=params)
        print("query results:" , results)
        await app.state.db_driver.pool.close()



