import os
from configparser import ConfigParser

ENV = os.getenv('OBSERVER_ENV', 'DEV')
app_config: ConfigParser = ConfigParser()
this_dir = os.path.dirname(__file__)
app_config.read(filenames=[os.path.join(this_dir, '../config/config.ini'), os.path.join(this_dir, f'../config/config.{ENV}.ini')])

if 'kafka' not in app_config:
    raise RuntimeError("kafka config is missing")

kafka_config: dict = {
    'host': app_config.get("kafka", "host"),
    "topic_name": app_config.get("kafka", "topic_name"),
    'api_version': tuple(map(lambda x: int(x), app_config.get("kafka", "api_version").split("."))),
    'ssl_ca_path': os.path.join(this_dir, f'../config/{app_config.get("kafka", "ssl_ca_file")}'),
    'ssl_cert_path': os.path.join(this_dir, f'../config/{app_config.get("kafka", "ssl_cert_file")}'),
    'ssl_key_path': os.path.join(this_dir, f'../config/{app_config.get("kafka", "ssl_key_file")}')
}
