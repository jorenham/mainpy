# pyright: reportPrivateUsage=false

import asyncio
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

import pytest

import mainpy as mp


_F = TypeVar('_F', bound=Callable[..., Any])


def _patch_module(monkeypatch: pytest.MonkeyPatch, module: str):
    # Patch the module name in the frame
    frame = inspect.currentframe()
    assert frame is not None
    monkeypatch.setitem(frame.f_globals, '__name__', module)

    def __patch_module(fn: _F) -> _F:
        # Patch the module name in the function
        monkeypatch.setattr(fn, '__module__', module)
        return fn

    return __patch_module


@pytest.fixture()
def no_uvloop():
    orig = mp._infer_uvloop
    mp._infer_uvloop = lambda: False

    try:
        yield
    finally:
        mp._infer_uvloop = orig


def test_not_main(monkeypatch: pytest.MonkeyPatch):
    @mp.main
    @_patch_module(monkeypatch, 'spam')
    def app():
        pytest.fail('not main')

    assert callable(app)


def test_sync(monkeypatch: pytest.MonkeyPatch):
    @mp.main(is_async=False)
    @_patch_module(monkeypatch, '__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_sync_implicit(monkeypatch: pytest.MonkeyPatch):
    @mp.main
    @_patch_module(monkeypatch, '__main__')
    def app():
        return 'spam'

    assert app == 'spam'


def test_async(monkeypatch: pytest.MonkeyPatch):
    @mp.main(is_async=True, use_uvloop=False)
    @_patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(asyncio.get_event_loop_policy(),
                      asyncio.DefaultEventLoopPolicy)


def test_async_implicit(no_uvloop, monkeypatch: pytest.MonkeyPatch):
    @mp.main
    @_patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'
    assert isinstance(asyncio.get_event_loop_policy(),
                      asyncio.DefaultEventLoopPolicy)


def test_async_implicit_uvloop(monkeypatch: pytest.MonkeyPatch):
    @mp.main
    @_patch_module(monkeypatch, '__main__')
    async def app():
        return await asyncio.sleep(0, 'spam')

    assert app == 'spam'

    import uvloop

    assert isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy)
