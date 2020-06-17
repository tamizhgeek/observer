import os
from typing import Tuple

import yaml

from source.checks import Check

this_dir = os.path.dirname(__file__)

config_dir = os.getenv("OBSERVER_CONFIG_DIR", os.path.join(this_dir, "../config"))


def dict_to_check_tuple(check_config: dict) -> Tuple[Check, int]:
    if check_config.get('url') is None or check_config.get('frequency') is None:
        raise RuntimeError("Each check config should have url and frequency attributes")
    return Check(url=check_config['url'], regex_checks=check_config.get('regex')), check_config['frequency']


def load_checks() -> set:
    with open(os.path.join(config_dir, "checks.yml"), "r") as f:
        checks = yaml.safe_load(f.read())
    if checks is None:
        raise RuntimeError("there is a problem with loading check configuration")
    return set(map(dict_to_check_tuple, checks))
