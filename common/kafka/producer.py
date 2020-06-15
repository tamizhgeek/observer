from kafka import KafkaProducer

from common.config import kafka_config
from common.logging import logger


class KafkaP:
    def __init__(self, config=None):
        if config is None:
            config = kafka_config
        self.producer = KafkaProducer(
            ssl_certfile=config["ssl_cert_path"],
            ssl_keyfile=config["ssl_key_path"],
            ssl_cafile=config['ssl_ca_path'],
            security_protocol="SSL",
            bootstrap_servers=config['host']
        )

    def send(self, topic: str, data: bytes, error_callback=None):
        if error_callback is None:
            error_callback = self.error_callback
        self.producer.send(topic, data).add_errback(error_callback)

    @staticmethod
    def error_callback(ex):
        logger.error('Kafka producer send failed', exc_info=ex)
