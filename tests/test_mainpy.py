import asyncio

import pytest

import mainpy as mp


def patch_module(module):
    def _patch_module(fn):
        fn.__module__ = module
        return fn
    return _patch_module


@pytest.fixture
def no_uvloop():
    orig = mp._infer_uvloop  # noqa
    mp._infer_uvloop = lambda: False
    yield
    mp._infer_uvloop = orig


def test_not_main():
    @mp.main
    @patch_module('spam')
    def app():
        assert False

    assert callable(app)


def test_sync():
    @mp.main(is_async=False)
    @patch_module('__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_sync_implicit():
    @mp.main
    @patch_module('__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_async():
    @mp.main(is_async=True, use_uvloop=False)
    @patch_module('__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy
    )


def test_async_implicit(no_uvloop):
    @mp.main
    @patch_module('__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy
    )


def test_async_implicit_uvloop():
    @mp.main
    @patch_module('__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'

    import uvloop
    assert isinstance(
        asyncio.get_event_loop_policy(),
        uvloop.EventLoopPolicy
    )
