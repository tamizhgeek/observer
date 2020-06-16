import os

import yaml

from source.checks import Check

this_dir = os.path.dirname(__file__)


def dict_to_check_tuple(check_config: dict):
    if check_config.get('url') is None or check_config.get('frequency') is None:
        raise RuntimeError("Each check config should have url and frequency attributes")
    return Check(url=check_config['url'], regex_checks=check_config.get('regex')), check_config['frequency']


def load_checks() -> set:
    with open(os.path.join(this_dir, "../config/checks.yml"), "r") as f:
        checks = yaml.safe_load(f.read())
    if checks is None:
        raise RuntimeError("there is a problem with loading check configuration")
    return set(map(dict_to_check_tuple, checks))
