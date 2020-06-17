from typing import Coroutine

from aiokafka import AIOKafkaProducer
from kafka.errors import KafkaTimeoutError

from common.kafka.ssl import create_ssl_context
from common.logging import logger


async def producer(kafka_config: dict) -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        ssl_context=create_ssl_context(kafka_config),
        security_protocol="SSL",
        bootstrap_servers=kafka_config['host'],
        enable_idempotence=True
    )
    await producer.start()
    return producer


async def send(p: AIOKafkaProducer, topic: str, data: bytes, retried=False) -> None:
    try:
        future = await p.send(topic, data)
        await future
    except KafkaTimeoutError as e:
        logger.error("kafka producer send failed", exc_info=e)
        # In case of timeout, we retry once
        if not retried:
            await send(p, topic, data, retried=True)
        else:
            raise e
