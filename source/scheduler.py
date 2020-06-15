import asyncio

from common.kafka.producer import KafkaP
from common.logging import logger
from common.util import url_to_topic
from source.checks import Check
from source.client import HttpClientLike


async def schedule(client: HttpClientLike, kafka_p: KafkaP, check: Check, repeat_in_s: int):
    logger.info(f"scheduling observer for {check.url} every {repeat_in_s} seconds")
    while True:
        result = await check.execute(client)
        logger.debug(f"Results for url: {check.url} - results:{result.to_json()}")
        await kafka_p.send(url_to_topic(check.url, 'http_check'), result.to_json())
        await asyncio.sleep(repeat_in_s)
        logger.info(f"repeating check for {check.url} after {repeat_in_s} seconds")
