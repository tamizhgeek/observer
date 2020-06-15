from kafka import KafkaProducer

from common.config import kafka_config
from common.logging import logger


class KafkaP:
    def __init__(self, host: str = kafka_config['host']):
        self.producer = KafkaProducer(bootstrap_servers=host)

    def send(self, topic: str, data: bytearray, error_callback=None):
        if error_callback is None:
            error_callback = self.error_callback
        self.producer.send(topic, data).add_errback(error_callback)

    @staticmethod
    def error_callback(ex):
        logger.error('Kafka producer send failed', exc_info=ex)
