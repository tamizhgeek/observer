import os
from configparser import ConfigParser

ENV = os.getenv('OBSERVER_ENV', 'DEV')
app_config: ConfigParser = ConfigParser()
this_dir = os.path.dirname(__file__)
app_config.read(filenames=[os.path.join(this_dir, '../config/config.ini'), os.path.join(this_dir, f'../config/config.{ENV}.ini')])

if 'kafka' not in app_config:
    raise RuntimeError("kafka config is missing")

kafka_config: dict = {
    'host': app_config.get("kafka", "host")
}
