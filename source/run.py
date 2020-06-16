import asyncio
from typing import Set, Tuple

from aiohttp import ClientSession

from common.checks_config import load_checks
from common.config import load_kafka_config
from common.kafka.producer import producer
from source.checks import Check
from source.client import AsyncHttpClient
from source.scheduler import schedule


async def main(kafka_config: dict, checks: Set[Tuple[Check, int]]):
    async with ClientSession() as session:
        client = AsyncHttpClient(session)
        tasks = []
        kafka_producer = await producer(kafka_config)
        try:
            for check, frequency_in_s in checks:
                tasks.append(schedule(client, kafka_config, kafka_producer, check, frequency_in_s))
            await asyncio.gather(*tasks)
        finally:
            await kafka_producer.flush()
            await kafka_producer.stop()


def run():
    kafka_config = load_kafka_config()
    checks = load_checks()
    asyncio.run(main(kafka_config, checks))


if __name__ == "__main__":
    run()
