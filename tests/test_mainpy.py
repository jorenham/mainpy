import sys
import asyncio
import pytest

import mainpy as mp


def patch_module(monkeypatch, module):
    # Patch the module name in the frame
    frame = sys._getframe(1).f_back  # noqa
    assert frame is not None
    f_globals = frame.f_globals
    monkeypatch.setitem(f_globals, '__name__', module)

    def _patch_module(fn):
        # Patch the module name in the function
        monkeypatch.setattr(fn, '__module__', module)
        return fn

    return _patch_module



@pytest.fixture
def no_uvloop():
    orig = mp._infer_uvloop  # noqa
    mp._infer_uvloop = lambda: False
    yield
    mp._infer_uvloop = orig


def test_not_main(monkeypatch):
    @mp.main
    @patch_module(monkeypatch, 'spam')
    def app():
        assert False

    assert callable(app)


def test_sync(monkeypatch):
    @mp.main(is_async=False)
    @patch_module(monkeypatch, '__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_sync_implicit(monkeypatch):
    @mp.main
    @patch_module(monkeypatch, '__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_async(monkeypatch):
    @mp.main(is_async=True, use_uvloop=False)
    @patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy
    )


def test_async_implicit(no_uvloop, monkeypatch):
    @mp.main
    @patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy
    )


def test_async_implicit_uvloop(monkeypatch):
    @mp.main
    @patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'

    import uvloop
    assert isinstance(
        asyncio.get_event_loop_policy(),
        uvloop.EventLoopPolicy
    )
