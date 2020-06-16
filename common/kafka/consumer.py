import json

from aiokafka import AIOKafkaConsumer

from common.kafka.ssl import create_ssl_context


async def consumer(kafka_config: dict):
    consumer = AIOKafkaConsumer(
        kafka_config['topic_name'],
        group_id="observer-consumer",
        ssl_context=create_ssl_context(kafka_config),
        security_protocol="SSL",
        bootstrap_servers=kafka_config['host'],
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    await consumer.start()
    return consumer