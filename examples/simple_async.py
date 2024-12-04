import asyncio

from mainpy import main


@main
async def async_app() -> str:
    return await asyncio.sleep(1, '\U0001f40c')


print('Result of `async_app()`:', repr(async_app))
