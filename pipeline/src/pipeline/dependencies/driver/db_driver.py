import logging
import time
import typing

import psycopg
from psycopg_pool import AsyncConnectionPool

from pipeline.configuration import ConnectionConfig
from pipeline.dependencies.driver.db_config import DBConfig
from pipeline.dependencies.driver.table_info import (dynamic_data_statements,
                                                     meta_data_statements)


class DbDriver:
    name: str
    pool: AsyncConnectionPool
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, connection_config: ConnectionConfig):
        self.logger = logger
        if connection_config.localhost:
            self.logger.info("starting db driver using localhost connection")
            address = DBConfig().get_localhost_connection_pool_address()
        elif connection_config.compose:
            self.logger.info("starting db driver using compose connection")
            address = DBConfig().get_compose_connection_pool_address()
        self.pool = AsyncConnectionPool(address)

    async def insert_meta(self, data: list[tuple], table_name: str):
        self.logger.info(f"Inserting data for {table_name}")
        query_statement = meta_data_statements[table_name]
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.executemany(query_statement, data)
        except Exception as e:
            print(f"Pipeline aborted: {e}")
            await conn.rollback()
        except psycopg.errors.UniqueViolation as e:
            self.logger.warning(
                f"you are trying to insert duplicate key to {table_name}, expection: {e}"
            )

    async def insert_streaming_data(
            self, table_name: str, data: list[tuple], batch_size: int = 500
    ):
        total_rows = len(data)
        query_statement = dynamic_data_statements[table_name]

        for i in range(0, total_rows, batch_size):
            batched = data[i: i + batch_size]
            min_time = batched[0][0]
            max_time = batched[-1][0]

            conn = None
            try:
                async with self.pool.connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.executemany(query_statement, batched)

            except psycopg.errors.UniqueViolation as e:
                self.logger.warning(
                    f"Duplicate key insert attempted for {table_name}, exception: {e}"
                )
                if conn:
                    await conn.rollback()  # Rollback after unique violation

            except Exception as e:
                print(f"Pipeline aborted: {e}")
                if conn:
                    await conn.rollback()

            else:
                self.logger.info(
                    f"Inserted {len(batched)} rows to {table_name} between: {min_time} -> {max_time}"
                )

    async def query_data(self, query: str, params: list[typing.Any]) -> list[tuple]:
        # query_statement = query.generate_query()
        start_time = time.perf_counter()
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()
            await conn.commit()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        self.logger.info(
            f"Data retrieval completed in {elapsed_time:.2f} seconds. Retrieved {len(rows)} rows, with query_statement: {query} "
        )
        return rows
