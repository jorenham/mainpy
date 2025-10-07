from __future__ import annotations

import os
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, TypeVar, cast, overload


if TYPE_CHECKING:
    import contextvars
    from collections.abc import Coroutine
    from typing import TypeGuard

    from typing_extensions import Never

__all__ = ('main',)

_R = TypeVar('_R')
_R_co = TypeVar('_R_co', covariant=True)
_F = TypeVar('_F', bound=Callable[[], object])


def _infer_debug() -> bool:
    flags = sys.flags

    if flags.debug or flags.dev_mode:
        return True

    if '--debug' in sys.argv[1:]:
        return True

    env_debug_str = os.environ.get('DEBUG', '0')
    try:
        env_debug = int(env_debug_str)
    except ValueError as e:
        errmsg = f'Invalid value for `DEBUG` env var: {env_debug_str!r}'
        raise OSError(errmsg) from e

    return bool(env_debug)


def _infer_uvloop() -> bool:
    """Check whether uvloop is installed."""
    if 'uvloop' in sys.modules:
        return True

    import importlib.util

    return importlib.util.find_spec('uvloop') is not None


def _enable_debug() -> None:
    """Enable debug mode."""
    env = os.environ

    if not env.get('PYTHONWARNINGS'):
        import warnings

        warnings.simplefilter('always')

    if not (env.get('PYTHONDEVMODE') or env.get('PYTHONFAULTHANDLER')):
        import faulthandler

        faulthandler.enable()


class _HasCallbackFunction(Protocol[_R_co]):
    __module__: str

    @property
    def callback(self, /) -> Callable[[], _R_co]: ...
    def __call__(self, /) -> _R_co: ...


def _is_click_cmd(
    func: _HasCallbackFunction[object] | _F,
    /,
) -> TypeGuard[_HasCallbackFunction[_F]]:
    return func.__module__ == 'click.core' and hasattr(func, 'callback')


@overload
def _unwrap_click(func: _HasCallbackFunction[_R], /) -> Callable[[], _R]: ...
@overload
def _unwrap_click(func: _F, /) -> _F: ...
def _unwrap_click(func: _HasCallbackFunction[object] | _F, /) -> _F | object:
    if _is_click_cmd(func):
        return func.callback
    return func


def _is_main_func(func: Callable[[], object], /) -> bool:
    return _unwrap_click(func).__module__ == '__main__'


def _run_async(
    coro: Coroutine[object, object, object],
    /,
    *,
    debug: bool,
    use_uvloop: bool,
    context: contextvars.Context | None,
) -> object:
    import asyncio

    if sys.version_info >= (3, 11):
        loop_factory = None
        if use_uvloop:
            import uvloop

            loop_factory = uvloop.new_event_loop

        with asyncio.Runner(debug=debug, loop_factory=loop_factory) as runner:
            result = runner.run(coro, context=context)
    else:
        if use_uvloop:
            import uvloop

            uvloop.install()

        result = asyncio.run(coro, debug=debug)

    return result


@overload
def main(
    func: None = None,
    /,
    *,
    debug: bool | None = None,
    is_async: bool | None = None,
    use_uvloop: bool | None = None,
    context: contextvars.Context | None = None,
) -> Callable[[_F], _F]: ...
@overload
def main(
    func: _F,
    /,
    *,
    debug: bool | None = None,
    is_async: bool | None = None,
    use_uvloop: bool | None = None,
    context: contextvars.Context | None = None,
) -> _F: ...
def main(
    func: _F | None = None,
    /,
    *,
    debug: bool | None = None,
    is_async: bool | None = None,
    use_uvloop: bool | None = None,
    context: contextvars.Context | None = None,
) -> Callable[[_F], _F] | _F:
    """
    Decorate a function to be the main entrypoint.
    """
    if func is None:

        def _main(func_: _F, /) -> _F:
            return main(
                func_,
                debug=debug,
                is_async=is_async,
                use_uvloop=use_uvloop,
                context=context,
            )

        return _main

    if not callable(func):
        errmsg = f'expected a callable, got {type(func)}'
        raise TypeError(errmsg)

    if not _is_main_func(func):
        import inspect

        frame = inspect.currentframe()
        if not frame or frame.f_globals.get('__name__') != '__main__':
            return func

    if debug is None:
        debug = _infer_debug()
    if debug:
        _enable_debug()

    result = func()

    if is_async is False:
        return func
    if is_async is None:
        import asyncio

        if not asyncio.iscoroutine(result):
            return func

    coro = cast('Coroutine[object, object, object]', result)

    if use_uvloop is None:
        use_uvloop = _infer_uvloop()

    _ = _run_async(coro, debug=debug, use_uvloop=use_uvloop, context=context)

    return func


@main
def __main() -> Never:  # pyright: ignore[reportUnusedFunction]
    # this should never run
    raise AssertionError
