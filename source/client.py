from aiohttp import ClientSession, ClientResponseError, ClientConnectionError

from common.logging import logger
from source.checks import CheckResponse


class HttpClientLike:
    def get(self, url, retries) -> CheckResponse:
        raise NotImplementedError()


class AsyncHttpClient(HttpClientLike):
    def __init__(self, session: ClientSession):
        self.session = session

    async def get(self, url, retries) -> CheckResponse:
        try:
            response = await self.session.get(url)
            text = await response.text()
            return CheckResponse(response.status, text, None)
        except ClientResponseError as e:
            return CheckResponse(e.status, None, e.message)
        except ClientConnectionError as e:
            if retries > 0:
                logger.error(f"Request failed while GET on url: {url}. Retrying")
                await self.get(self.session, retries - 1)
            else:
                raise e