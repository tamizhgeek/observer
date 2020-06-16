from aiokafka.helpers import create_ssl_context as _create_ssl_context


def create_ssl_context(kafka_config):
    return _create_ssl_context(certfile=kafka_config["ssl_cert_path"],
                              keyfile=kafka_config["ssl_key_path"],
                              cafile=kafka_config['ssl_ca_path'])
