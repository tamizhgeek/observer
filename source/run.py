import asyncio

from aiohttp import ClientSession

from common.checks_config import checks
from common.kafka.producer import KafkaP
from source.checks import Check
from source.client import AsyncHttpClient
from source.scheduler import schedule


async def main():
    async with ClientSession() as session:
        client = AsyncHttpClient(session)
        kafka_producer = KafkaP()
        tasks = []
        for check, frequency_in_s in checks:
            tasks.append(schedule(client, kafka_producer, check, frequency_in_s))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
