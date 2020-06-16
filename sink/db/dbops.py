import datetime
import json
from typing import Iterable

import asyncpg
from asyncpg import Connection
from asyncpg.exceptions import UndefinedTableError, UniqueViolationError
from asyncpg.pool import Pool

from common.logging import logger


async def init_pool(conn_string: str = None) -> Pool:
    return await asyncpg.create_pool(dsn=conn_string, init=set_custom_encoding)


async def set_custom_encoding(conn: Connection):
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )


async def connect(conn_string: str = None) -> Connection:
    conn = await asyncpg.connect(dsn=conn_string)
    await set_custom_encoding(conn)
    return conn


def table_ddl(table_name: str, schema: str) -> dict:
    return dict(
        http_check_results=f'CREATE TABLE {schema}.{table_name} ('
                           f'id varchar(36) PRIMARY KEY NOT NULL, '
                           f'kafka_partition_offset_id varchar(20) NOT NULL, '
                           f'url text NOT NULL, '
                           f'response_code int NOT NULL, '
                           f'response_time float NOT NULL, '
                           f'regex_checks json, '
                           f'errors json, '
                           f'created_at timestamptz NOT NULL'
                           f')',
        http_check_results_index=f'CREATE INDEX url_idx ON {schema}.{table_name}(url)'
    )


# executemany is a problem if we have duplicate check results in the batch - it will then fail the whole batch
# Our kafka consumer works on `At least once` semantics, so duplicates are possible. Hence we insert batches inside
# large transaction blocks.
async def insert_many(conn: Connection, schema: str, table: str, columns: list, values: Iterable[list]):
    num_columns = len(columns)
    place_holders = ",".join(list(map(lambda x: f'${x}', range(1, num_columns + 1))))
    columns_str = ",".join(columns)
    insert_query = f"INSERT INTO {schema}.{table} ({columns_str}) VALUES ({place_holders}) ON CONFLICT DO NOTHING"
    logger.info(f"executing query {insert_query}")
    logger.info(values)
    await conn.executemany(insert_query, values)


async def create_table_if_not_exists(conn: Connection, schema: str, table: str):
    table_exists_bool = await table_exists(conn, schema, table)
    if not table_exists_bool:
        for table_name, ddl in table_ddl(table, schema).items():
            logger.info(f"creating table {table_name}")
            await conn.execute(ddl)


async def table_exists(conn: Connection, schema: str, table: str) -> bool:
    try:
        await conn.fetch(f"SELECT * from {schema}.{table} limit 1")
        return True
    except UndefinedTableError as e:
        logger.warning("table doesn't exist", exc_info=e)
        return False
