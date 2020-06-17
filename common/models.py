import datetime
import json
import time
import uuid
from typing import Optional


class CheckResult:
    def __init__(self, url: str, code: int, response_time: float, regex_checks: dict, errors: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.response_code = code
        self.url = url
        self.response_time = response_time
        self.regex_checks = regex_checks
        self.errors = errors
        self.created_at = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    def to_json(self) -> str:
        return json.dumps(dict(filter(lambda item: item[1] is not None, self.__dict__.items())))