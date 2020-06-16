import re
from typing import Optional

from common.logging import logger
from common.models import CheckResult
from source.client import HttpClientLike


class Check:
    def __init__(self, url: str, regex_checks: Optional[list] = None):
        self.url = url
        self.regex_checks = regex_checks
        if self.regex_checks is not None:
            self.regex_checks = dict(
                map(lambda check: (check['name'], self.check_regex(check['pattern'])), regex_checks))

    async def execute(self, client: HttpClientLike) -> CheckResult:
        results = dict()
        logger.info(f"GET url: {self.url}")
        response = await client.get(self.url, retries=3)
        if self.regex_checks is not None:
            logger.info(f"executing extra regex checks for url: {self.url}")
            for name, check_func in self.regex_checks.items():
                logger.info(f"executing regex check : {name} for url: {self.url}")
                results[name] = check_func(response.body)
        return CheckResult(self.url, response.code, response.time, results, response.error)

    @staticmethod
    def check_regex(pattern: str) -> object:
        re_pattern = re.compile(pattern)

        def _match(text: str) -> bool:
            if text is None:
                return False
            match = re_pattern.match(text)
            return match is not None

        return _match
