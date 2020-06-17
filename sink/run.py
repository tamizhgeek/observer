import asyncio
import datetime
from typing import List, Coroutine

from aiokafka import ConsumerRecord
from asyncpg import Connection

from common.config import load_db_config, load_kafka_config
from common.kafka.consumer import consumer as kafka_consumer
from common.logging import logger
from sink.db.dbops import init_pool, insert_many, create_table_if_not_exists


def kafka_meta_id(message: ConsumerRecord) -> str:
    return f"{message.partition}-{message.offset}"


async def insert_into_db(conn: Connection, schema_name: str, table_name: str, check_results: List[dict]) -> None:
    if len(check_results) > 0:
        columns = check_results[0].keys()
        for check_result in check_results:
            if 'created_at' in check_result:
                check_result['created_at'] = datetime.datetime.fromisoformat(check_result['created_at'])
        values = list(map(lambda x: list(x.values()), check_results))
        await insert_many(conn, schema_name, table_name, columns, values)


async def main(db_config: dict, kafka_config: dict, buffer_limit: int = 100):
    pool = await init_pool(db_config['conn_string'])
    consumer = await kafka_consumer(kafka_config)
    async with pool.acquire() as connection:
        await create_table_if_not_exists(connection, db_config['schema'], db_config['table'])
        try:
            buffer = []
            async for message in consumer:
                logger.info(f"received message : {message}")
                value = message.value
                value['kafka_partition_offset_id'] = kafka_meta_id(message)
                buffer.append(value)
                if len(buffer) >= buffer_limit:
                    logger.info("Buffer is full. Going to attempt insert into table")
                    await insert_into_db(connection, db_config['schema'], db_config['table'], buffer)
                    await consumer.commit()
                    buffer.clear()
        finally:
            await consumer.stop()
    await pool.close()


def run():
    kafka_config = load_kafka_config()
    db_config = load_db_config()
    asyncio.run(main(db_config, kafka_config))


if __name__ == "__main__":
    run()
