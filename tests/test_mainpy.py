# pyright: reportPrivateUsage=false
from __future__ import annotations

import asyncio
import importlib.util
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

import pytest

import mainpy as mp


if TYPE_CHECKING:
    from collections.abc import Generator


_F = TypeVar('_F', bound=Callable[..., object])


def _patch_module(
    monkeypatch: pytest.MonkeyPatch,
    module: str,
) -> Callable[[_F], _F]:
    # Patch the module name in the frame
    frame = inspect.currentframe()
    assert frame is not None
    monkeypatch.setitem(frame.f_globals, '__name__', module)

    def __patch_module(fn: _F, /) -> _F:
        # Patch the module name in the function
        monkeypatch.setattr(fn, '__module__', module)
        return fn

    return __patch_module


@pytest.fixture()
def no_uvloop() -> Generator[Callable[[], bool], None, None]:
    orig = mp._infer_uvloop
    mp._infer_uvloop = lambda: False

    try:
        yield orig
    finally:
        mp._infer_uvloop = orig


def test_not_main(monkeypatch: pytest.MonkeyPatch) -> None:
    @mp.main
    @_patch_module(monkeypatch, 'spam')
    def app() -> None:
        pytest.fail('not main')

    assert callable(app)


def test_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    result: list[object] = [None]

    @mp.main(is_async=False)
    @_patch_module(monkeypatch, '__main__')
    def app() -> None:
        result[0] = 'spam'

    assert result[0] == 'spam'
    assert callable(app)


def test_sync_implicit(monkeypatch: pytest.MonkeyPatch) -> None:
    result: list[object] = [None]

    @mp.main
    @_patch_module(monkeypatch, '__main__')
    def app() -> None:
        result[0] = 'spam'

    assert result[0] == 'spam'
    assert callable(app)


def test_async(monkeypatch: pytest.MonkeyPatch) -> None:
    result: list[object] = [None]

    @mp.main(is_async=True, use_uvloop=False)
    @_patch_module(monkeypatch, '__main__')
    async def app() -> None:
        result[0] = await asyncio.sleep(0, 'spam')

    assert result[0] == 'spam'
    assert callable(app)
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy,
    )


def test_async_implicit(
    no_uvloop: None,  # pyright: ignore[reportUnusedParameter]
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result: list[object] = [None]

    @mp.main
    @_patch_module(monkeypatch, '__main__')
    async def app() -> None:
        result[0] = await asyncio.sleep(0, 'spam')

    assert result[0] == 'spam'
    assert callable(app)
    assert isinstance(
        asyncio.get_event_loop_policy(),
        asyncio.DefaultEventLoopPolicy,
    )


def test_async_implicit_uvloop(monkeypatch: pytest.MonkeyPatch) -> None:
    result: list[object] = [None]

    @mp.main
    @_patch_module(monkeypatch, '__main__')
    async def loop_module() -> None:
        await asyncio.sleep(0)
        loop = asyncio.get_running_loop()
        result[0] = loop.__module__.split('.')[0]

    assert result[0]
    assert isinstance(result[0], str)
    assert callable(loop_module)

    if importlib.util.find_spec('uvloop') is None:
        assert not mp._infer_uvloop()
        assert result[0] == 'asyncio'
    else:
        assert mp._infer_uvloop()
        assert result[0] == 'uvloop'
