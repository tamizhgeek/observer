import asyncio

import pytest
from aiohttp import ClientSession

from common.kafka.producer import KafkaP
from common.util import url_to_topic
from source.checks import Check
from source.client import AsyncHttpClient, HttpClientLike
from source.scheduler import schedule


@pytest.fixture
async def http_client():
    async with ClientSession() as session:
        yield AsyncHttpClient(session)


class MockKafkaProducer(KafkaP):
    def __init__(self):
        self.sent_messages = dict()

    async def send(self, topic: str, data: bytearray, error_callback=None):
        if topic not in self.sent_messages:
            self.sent_messages[topic] = [data]
        else:
            self.sent_messages[topic].append(data)


@pytest.fixture
def kafka_producer():
    return MockKafkaProducer()


@pytest.mark.asyncio
async def test_scheduled_check_execution_times(http_client: HttpClientLike, kafka_producer: MockKafkaProducer):
    check = Check("https://postman-echo.com/get", {'check_postman_echo': '.*host.*:.*postman\-echo.com'})
    repeat_secs = 1
    num_repeat = 3
    try:
        await asyncio.wait_for(schedule(http_client, kafka_producer, check, repeat_secs), timeout=(repeat_secs * num_repeat) + 0.1)
    except asyncio.TimeoutError:
        print('timeout!')
        assert len(kafka_producer.sent_messages[url_to_topic('https://postman-echo.com/get')]) == num_repeat
