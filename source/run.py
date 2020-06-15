import asyncio

from aiohttp import ClientSession

from common.kafka.producer import KafkaP
from source.checks import Check
from source.client import AsyncHttpClient
from source.scheduler import schedule


async def main():
    async with ClientSession() as session:
        client = AsyncHttpClient(session)
        kafka_producer = KafkaP()
        tasks = []
        for url, wait_in_s in {"https://aiven.io": 2, "https://google.com": 3, "https://eyeem.com": 5, "https://fb.com": 50}.items():
            check = Check(url, None)
            tasks.append(schedule(client, kafka_producer, check, wait_in_s))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
