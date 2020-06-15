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

    def __str__(self):
        checks_str = ",".join(list(map(lambda check, result: f"${check} returned {result}", self.regex_checks)))
        return f"Url:{self.url},code:{self.code},time_taken:{self.time},regex_checks:{checks_str},errors:{self.errors}"

class Check:
    def __init__(self, url: str, checks: Optional[dict] = None):
        self.url = url
        self.checks = checks

    async def execute(self, client: HttpClientLike):
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
