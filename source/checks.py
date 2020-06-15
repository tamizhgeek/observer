import json
import re
import time
from typing import Optional

from common.logging import logger
from source.client import HttpClientLike, ClientResponse


class CheckResult:
    def __init__(self, url: str, code: int, time: float, regex_checks: dict, errors: Optional[str] = None):
        self.code = code
        self.url = url
        self.time = time
        self.regex_checks = regex_checks
        self.errors = errors

    def to_json(self):
        return json.dumps(dict(filter(lambda item: item[1] is not None, self.__dict__.items())))


class Check:
    def __init__(self, url: str, checks: Optional[dict] = None):
        self.url = url
        self.checks = checks
        if self.checks is not None:
            self.checks = dict(map(lambda check: (check[0], self.check_regex(check[1])), checks.items()))

    async def execute(self, client: HttpClientLike) -> CheckResult:
        results = dict()
        logger.info(f"GET url: {self.url}")
        response = await client.get(self.url, retries=3)
        if self.checks is not None:
            logger.info(f"executing extra regex checks for url: {self.url}")
            for name, check_func in self.checks.items():
                logger.info(f"executing regex check : {name} for url: {self.url}")
                results[name] = check_func(response.body)
        return CheckResult(self.url, response.code, response.time, results, response.error)

    @staticmethod
    def check_regex(pattern: str) -> object:
        re_pattern = re.compile(pattern)

        def _match(text: str) -> bool:
            match = re_pattern.match(text)
            return match is not None

        return _match
