import pytest
from aiohttp import ClientSession

from source.checks import Check
from source.client import AsyncHttpClient


@pytest.fixture
async def http_client():
    async with ClientSession() as session:
        yield AsyncHttpClient(session)


@pytest.mark.asyncio
async def test_check_should_get_a_page_and_return_check_result(http_client):
    check = Check("https://postman-echo.com/get")
    result = await check.execute(http_client)
    assert result.response_code == 200
    assert result.url == "https://postman-echo.com/get"
    assert result.response_time > 0
    json_s = result.to_json()
    for expected in ['code', 'url', 'time', 'checks']:
        assert expected in json_s


@pytest.mark.asyncio
async def test_check_should_get_a_page_and_return_check_result_with_regex_checks(http_client):
    check = Check("https://postman-echo.com/get", [{'name': 'check_postman_echo', 'pattern': '.*host.*:.*postman-echo.com'}])
    result = await check.execute(http_client)
    assert result.response_code == 200
    assert result.url == "https://postman-echo.com/get"
    assert result.response_time > 0
    assert result.regex_checks.get('check_postman_echo')
    assert not result.regex_checks.get('non_existent_check')
    json_s = result.to_json()
    for expected in ['code', 'url', 'time', 'checks']:
        assert expected in json_s


@pytest.mark.asyncio
async def test_check_400_result(http_client):
    check = Check("https://postman-echo.com/status/400")
    result = await check.execute(http_client)
    assert result.response_code == 400
    assert result.url == "https://postman-echo.com/status/400"
    assert result.response_time > 0


@pytest.mark.asyncio
async def test_check_500_result(http_client):
    check = Check("https://postman-echo.com/status/500")
    result = await check.execute(http_client)
    assert result.response_code == 500
    assert result.url == "https://postman-echo.com/status/500"
    assert result.response_time > 0
