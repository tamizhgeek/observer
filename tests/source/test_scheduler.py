import asyncio

import pytest
from aiohttp import ClientSession
from aiokafka import AIOKafkaProducer

from common.config import load_kafka_config
from source.checks import Check
from source.client import AsyncHttpClient, HttpClientLike
from source.scheduler import schedule


@pytest.fixture
async def http_client():
    async with ClientSession() as session:
        yield AsyncHttpClient(session)


class MockKafkaProducer(AIOKafkaProducer):
    def __init__(self):
        self.sent_messages = dict()

    async def send(self, topic, value=None, key=None, partition=None,
            timestamp_ms=None, headers=None):
        if topic not in self.sent_messages:
            self.sent_messages[topic] = [value]
        else:
            self.sent_messages[topic].append(value)
        future = asyncio.get_running_loop().create_future()
        future.set_result(1)
        return future


@pytest.fixture
def kafka_producer():
    return MockKafkaProducer()

@pytest.fixture
def kafka_config():
    return load_kafka_config("TEST")


@pytest.mark.asyncio
async def test_scheduled_check_execution_times(http_client: HttpClientLike, kafka_producer: MockKafkaProducer, kafka_config: dict):
    check = Check("https://postman-echo.com/get", [{'name': 'check_postman_echo', 'pattern': '.*host.*:.*postman\-echo.com'}])
    repeat_secs = 1
    num_repeat = 3
    try:
        # timeout the never ending coroutine and make sure number of checks done is as expected
        await asyncio.wait_for(schedule(http_client, kafka_config, kafka_producer, check, repeat_secs), timeout=(repeat_secs * num_repeat) + repeat_secs)
    except asyncio.TimeoutError:
        print('timeout!')
        assert len(kafka_producer.sent_messages[kafka_config['topic_name']]) >= num_repeat


@pytest.mark.asyncio
async def test_scheduled_check_execution_times_with_multiple_checks(http_client: HttpClientLike,
                                                                    kafka_producer: MockKafkaProducer,
                                                                    kafka_config: dict):
    num_checks = 5
    repeat_secs = 1
    num_repeat = 3
    checks = []
    for _ in range(num_checks):
        checks.append(Check("https://postman-echo.com/get", [{'name': 'check_postman_echo', 'pattern': '.*host.*:.*postman\-echo.com'}]))
    try:
        # timeout the never ending coroutine and make sure number of checks done is as expected
        all_checks = map(lambda check: schedule(http_client, kafka_config, kafka_producer, check, repeat_secs), checks)
        await asyncio.wait_for(asyncio.gather(*all_checks), timeout=(repeat_secs * num_repeat) + repeat_secs)
    except asyncio.TimeoutError:
        print('timeout!')
        assert len(kafka_producer.sent_messages[kafka_config['topic_name']]) >= num_repeat * num_checks