import os
from configparser import ConfigParser
from typing import Optional

this_dir = os.path.dirname(__file__)
config_dir = os.getenv("OBSERVER_CONFIG_DIR", os.path.join(this_dir, "../config"))


def load_app_config(env: Optional[str] = None):
    app_config: ConfigParser = ConfigParser()
    filenames = [os.path.join(config_dir, 'config.ini')]
    if env is not None:
        filenames.append(os.path.join(config_dir, f'config.{env}.ini'))
    app_config.read(filenames)
    return app_config


def load_kafka_config(env: Optional[str] = None):
    app_config = load_app_config(env)
    if 'kafka' not in app_config:
        raise RuntimeError("kafka config is missing")
    for key in ['host', 'topic_name', 'api_version', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file']:
        if not app_config.has_option('kafka', key):
            raise RuntimeError(f"Kafka config key {key} is missing")
    return {
        'host': app_config.get("kafka", "host"),
        "topic_name": app_config.get("kafka", "topic_name"),
        'api_version': tuple(map(lambda x: int(x), app_config.get("kafka", "api_version").split("."))),
        'ssl_ca_path': os.path.join(config_dir, app_config.get("kafka", "ssl_ca_file")),
        'ssl_cert_path': os.path.join(config_dir, app_config.get("kafka", "ssl_cert_file")),
        'ssl_key_path': os.path.join(config_dir, app_config.get("kafka", "ssl_key_file"))
    }


def load_db_config(env: Optional[str] = None):
    app_config = load_app_config(env)
    if 'db' not in app_config:
        raise RuntimeError("db config is missing")
    for key in ['conn_string', 'schema', 'table']:
        if not app_config.has_option('db', key):
            raise RuntimeError(f"DB config key {key} is missing")
    return {
        'conn_string': app_config.get('db', 'conn_string'),
        'schema': app_config.get('db', 'schema'),
        'table': app_config.get('db', 'table')
    }
