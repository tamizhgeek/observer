import datetime
import uuid
from typing import Mapping

import pytest
from asyncpg import Record, Connection, UniqueViolationError

from common.config import load_db_config
from sink.db import fixtures
from sink.db.dbops import table_exists, connect, create_table_if_not_exists, insert_many


@pytest.fixture
def db_config(env: str = "TEST"):
    return load_db_config(env)


@pytest.fixture
async def db(env: str = "TEST"):
    config = load_db_config(env)
    db = await connect(config['conn_string'])
    await db.execute(f"DROP SCHEMA IF EXISTS {config['schema']} cascade")
    return db


@pytest.mark.asyncio
async def test_database_fixture_creation(db_config, db):
    schema = db_config['schema']
    # ensure the table is not present
    assert not await table_exists(db, schema, db_config['table'])
    # Run fixtures without destroying existing schema
    await fixtures.main(db_config, live=True)
    # ensure the table is present
    assert await table_exists(db, schema, db_config['table'])
    # Run fixtures after destroying existing schema
    await fixtures.main(db_config, live=True, destroy=True)
    # ensure the table is present
    assert await table_exists(db, schema, db_config['table'])


@pytest.mark.asyncio
async def test_pg_custom_encoding_json(db_config, db):
    await db.execute(f"CREATE SCHEMA {db_config['schema']}")
    await db.execute(f"CREATE TABLE IF NOT EXISTS {db_config['schema']}.test_json_custom_encoding(json_field json)")
    some_dict = {
        'hello': 'world',
        'test': 123,
    }
    await db.execute(f"INSERT INTO {db_config['schema']}.test_json_custom_encoding (json_field) VALUES ($1)", some_dict)
    row: Record = await db.fetch(f"SELECT json_field from {db_config['schema']}.test_json_custom_encoding LIMIT 1")
    assert row[0]['json_field'] == some_dict


@pytest.mark.asyncio
async def test_pg_custom_encoding_datetime(db_config, db):
    await db.execute(f"CREATE SCHEMA {db_config['schema']}")
    await db.execute(f"DROP TABLE IF EXISTS {db_config['schema']}.test_datetime_custom_encoding")
    await db.execute(
        f"CREATE TABLE IF NOT EXISTS {db_config['schema']}.test_datetime_custom_encoding(date_field timestamptz)")
    datetime_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    await db.execute(f"INSERT INTO {db_config['schema']}.test_datetime_custom_encoding (date_field) VALUES ($1)",
                     datetime_now)
    row: Record = await db.fetch(f"SELECT date_field from {db_config['schema']}.test_datetime_custom_encoding LIMIT 1")
    assert row[0]['date_field'] == datetime_now


@pytest.mark.asyncio
async def test_storing_check_results_to_db(db_config: Mapping[str, str], db: Connection):
    await db.execute(f"CREATE SCHEMA {db_config['schema']}")
    await create_table_if_not_exists(db, db_config['schema'], db_config['table'])
    await insert_many(db, db_config['schema'], db_config['table'],
                      ['id', 'url', 'response_code', 'response_time',
                       'regex_checks', 'errors', 'kafka_partition_offset_id', 'created_at'],
                      [
                          [str(uuid.uuid4()), 'https://google.com', 200, 1.3433, None, None, '2-45332',
                           datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)],
                          [str(uuid.uuid4()), 'https://google.com', 400, 1.3433, None, None, '2-45333',
                           datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)],
                          [str(uuid.uuid4()), 'https://google.com', 500, 1.3433, {'check1': True, 'check2': False}, None,
                           '2-45334', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)],
                      ]
                      )
    results = await db.fetch(f"SELECT * from {db_config['schema']}.{db_config['table']}")
    assert len(results) == 3


@pytest.mark.asyncio
async def test_ignore_on_duplicate_insert(db_config: Mapping[str, str], db: Connection):
    await db.execute(f"CREATE SCHEMA {db_config['schema']}")
    await create_table_if_not_exists(db, db_config['schema'], db_config['table'])
    uuid_str = str(uuid.uuid4())
    await insert_many(db, db_config['schema'], db_config['table'],
                      ['id', 'url', 'response_code', 'response_time',
                       'regex_checks', 'errors', 'kafka_partition_offset_id', 'created_at'],
                      [
                          [uuid_str, 'https://google.com', 200, 1.3433, None, None, '2-45332',
                           datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)],
                          [uuid_str, 'https://google.com', 500, 1.3433, {'check1': True, 'check2': False}, None,
                           '2-45334', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)],
                      ]
                      )
    results = await db.fetch(f"SELECT * from {db_config['schema']}.{db_config['table']}")
    assert len(results) == 1
