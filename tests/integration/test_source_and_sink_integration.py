import asyncio

import pytest

from sink.db.dbops import connect
from source.run import main as source_main
from sink.run import main as sink_main
from common.checks_config import load_checks
from common.config import load_db_config, load_kafka_config


@pytest.fixture
def db_config(env: str = "TEST"):
    return load_db_config(env)


@pytest.fixture
def kafka_config(env: str = "TEST"):
    return load_kafka_config(env)


@pytest.fixture
def checks_config():
    return load_checks()


@pytest.fixture
async def db(env: str = "TEST"):
    config = load_db_config(env)
    db = await connect(config['conn_string'])
    await db.execute(f"DROP SCHEMA IF EXISTS {config['schema']} cascade")
    return db


@pytest.mark.asyncio
async def test_source_and_sink_integration(db, db_config, kafka_config, checks_config):
    await db.execute(f"CREATE SCHEMA {db_config['schema']}")
    source_coro = source_main(kafka_config, checks_config)
    sink_coro = sink_main(db_config, kafka_config, buffer_limit=1)
    try:
        await asyncio.wait_for(asyncio.gather(source_coro, sink_coro), timeout=20)
    except asyncio.TimeoutError:
        print("timeout!!")
        results = await db.fetch(f"SELECT * from {db_config['schema']}.{db_config['table']}")
        assert len(results) > 1
