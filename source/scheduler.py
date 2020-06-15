import asyncio

from common.config import kafka_config
from common.kafka.producer import KafkaP
from common.logging import logger
from source.checks import Check
from source.client import HttpClientLike

TOPIC_NAME=kafka_config['topic_name']

async def schedule(client: HttpClientLike, kafka_p: KafkaP, check: Check, repeat_in_s: int):
    logger.info(f"scheduling observer for {check.url} every {repeat_in_s} seconds")
    while True:
        try:
            result = await check.execute(client)
            logger.info(f"Results for url: {check.url} - results:{result.to_json()}")
            kafka_p.send(TOPIC_NAME, bytes(result.to_json(), 'utf-8'))
            # kafka_p.producer.flush()
            await asyncio.sleep(repeat_in_s)
            logger.info(f"repeating check for {check.url} after {repeat_in_s} seconds")
        except KeyboardInterrupt as e:
            logger.error("interupted by user")
            return
