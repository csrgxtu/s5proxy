import pytest
import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector


PROXY_ADDR = 'socks5://username:password@localhost:3000'


@pytest.mark.asyncio
async def test_httpbin():
    url = 'http://httpbin.org/get'
    connector = ProxyConnector.from_url(PROXY_ADDR)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            assert await resp.json() is not False

@pytest.mark.asyncio
async def test_httpsbin():
    url = 'https://httpbin.org/get'
    connector = ProxyConnector.from_url(PROXY_ADDR)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            assert await resp.json() is not False

@pytest.mark.asyncio
async def test_httpsgist():
    url = 'https://gist.githubusercontent.com/csrgxtu/9c3d4303e262bf5333cc57ff11ea9105/raw/d57dcf1b58d76b5e543618e203f8bffb3fa141d9/gistfile1.txt'
    connector = ProxyConnector.from_url(PROXY_ADDR)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            print(await resp.text())