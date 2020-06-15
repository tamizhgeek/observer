import asyncio

from common.logging import logger
from source.checks import Check
from source.client import HttpClientLike


async def schedule(client: HttpClientLike, check: Check, repeat_in_s: int):
    logger.info(f"scheduling observer for {check.url} every {repeat_in_s} seconds")
    while True:
        result = await check.execute(client)
        logger.info(f"Results for url: {check.url} - results:{result}")
        await asyncio.sleep(repeat_in_s)
        logger.info(f"repeating check for {check.url} after {repeat_in_s} seconds")
