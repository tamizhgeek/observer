import time
from typing import Optional

from aiohttp import ClientSession, ClientConnectionError

from common.logging import logger


class HttpClientLike:
    def __init__(self):
        pass

    def get(self, url, retries):
        raise NotImplementedError()


class AsyncHttpClient(HttpClientLike):
    def __init__(self, session: ClientSession):
        self.session = session

    async def get(self, url, retries):
        try:
            start = time.perf_counter()
            response = await self.session.get(url)
            total_time = time.perf_counter() - start
            text = await response.text()
            if response.status < 400:
                return ClientResponse(response.status, total_time, text, None)
            else:
                return ClientResponse(response.status, total_time, None, response.reason)
        except ClientConnectionError as e:
            if retries > 0:
                logger.error(f"Request failed while GET on url: {url}. Retrying")
                await self.get(self.session, retries - 1)
            else:
                raise e


class ClientResponse:
    def __init__(self, code: int, time: float, body: Optional[str], error: Optional[str]):
        self.code = code
        self.body = body
        self.time = time
        self.error = error
