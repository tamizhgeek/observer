import asyncio

from aiokafka import AIOKafkaProducer

from common.kafka.producer import send as kafka_send
from common.logging import logger
from source.checks import Check
from source.client import HttpClientLike


async def schedule(client: HttpClientLike, kafka_config: dict, kafka_p: AIOKafkaProducer, check: Check, repeat_in_s: int):
    logger.info(f"scheduling observer for {check.url} every {repeat_in_s} seconds")
    while True:
        result = await check.execute(client)
        logger.info(f"Results for url: {check.url} - results:{result.to_json()}")
        await kafka_send(kafka_p, kafka_config['topic_name'], bytes(result.to_json(), 'utf-8'))
        await asyncio.sleep(repeat_in_s)
        logger.info(f"repeating check for {check.url} after {repeat_in_s} seconds")

