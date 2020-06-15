import json

from kafka import KafkaConsumer

from common.config import kafka_config
from common.logging import logger


class KafkaC:
    def __init__(self, config=None):
        if config is None:
            config = kafka_config
        self.consumer = KafkaConsumer(
            ssl_certfile=config["ssl_cert_path"],
            ssl_keyfile=config["ssl_key_path"],
            ssl_cafile=config['ssl_ca_path'],
            security_protocol="SSL",
            bootstrap_servers=config['host'],
            topics=list(config['topic_name']),
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def start_consuming(self):
        for message in self.consumer:
            yield message