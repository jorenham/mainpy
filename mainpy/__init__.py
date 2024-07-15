from __future__ import annotations

import asyncio
import os
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Protocol,
    TypeVar,
    cast,
    final,
    overload,
)


if TYPE_CHECKING:
    import contextvars

if sys.version_info < (3, 11):
    from typing_extensions import Never, TypeAlias
else:
    from typing import Never, TypeAlias

__all__ = ('main',)

_R = TypeVar('_R')
_F = TypeVar('_F', bound=Callable[[], Any])

_SFunc: TypeAlias = Callable[[], _R]
_AFunc: TypeAlias = Callable[[], Coroutine[Any, Any, _R]]


def _infer_debug() -> bool:
    flags = sys.flags

    if flags.debug or flags.dev_mode:
        return True

    if '--debug' in sys.argv[1:]:
        return True

    env_debug = os.environ.get('DEBUG', '0')
    try:
        env_debug = int(env_debug)
    except ValueError as e:
        errmsg = f'Invalid value for `DEBUG` env var: {env_debug!r}'
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


@final
class _MainDecorator(Protocol):
    @overload
    def __call__(self, func: _AFunc[_R], /) -> _AFunc[_R] | _R: ...
    @overload
    def __call__(self, func: _SFunc[_R], /) -> _SFunc[_R] | _R: ...


@overload
def main(
    func: None = ...,
    /,
    *,
    debug: bool | None = ...,
    is_async: bool | None = ...,
    use_uvloop: bool | None = ...,
    context: contextvars.Context | None = ...,
) -> _MainDecorator: ...
@overload
def main(
    func: _AFunc[_R],
    /,
    *,
    debug: bool | None = ...,
    is_async: bool | None = ...,
    use_uvloop: bool | None = ...,
    context: contextvars.Context | None = ...,
) -> _AFunc[_R] | _R: ...
@overload
def main(
    func: _SFunc[_R],
    /,
    *,
    debug: bool | None = ...,
    is_async: bool | None = ...,
    use_uvloop: bool | None = ...,
    context: contextvars.Context | None = ...,
) -> _SFunc[_R] | _R: ...
def main(
    func: _AFunc[_R] | _SFunc[_R] | None = None,
    /,
    *,
    debug: bool | None = None,
    is_async: bool | None = None,
    use_uvloop: bool | None = None,
    context: contextvars.Context | None = None,
) -> _MainDecorator | _AFunc[_R] | _SFunc[_R] | _R:
    """
    Decorate a function to be the main entrypoint.
    """
    if func is None:
        def _main(_func: _F, /) -> _F | object:
            return main(
                _func,
                debug=debug,
                is_async=is_async,
                use_uvloop=use_uvloop,
                context=context,
            )

        return cast(_MainDecorator, _main)

    if not callable(func):
        errmsg = f'expected a callable, got {type(func)}'
        raise TypeError(errmsg)

    if func.__module__ != '__main__':
        import inspect

        frame = inspect.currentframe()
        if not frame or frame.f_globals.get('__name__') != '__main__':
            return func

    if debug or (debug is None and _infer_debug()):
        _enable_debug()

    if is_async is False or (
        is_async is None
        and not asyncio.iscoroutinefunction(func)
    ):
        return cast(_R, func())

    if use_uvloop is None:
        use_uvloop = _infer_uvloop()

    if sys.version_info < (3, 11):
        if use_uvloop:
            import uvloop  # pyright: ignore[reportMissingImports]

            uvloop.install()  # pyright: ignore[reportUnknownMemberType]

        return asyncio.run(cast(Coroutine[Any, Any, _R], func()), debug=debug)

    loop_factory = None
    if use_uvloop:
        import uvloop

        loop_factory = uvloop.new_event_loop

    with asyncio.Runner(debug=debug, loop_factory=loop_factory) as runner:
        return runner.run(func(), context=context)


@main
def __main() -> Never:  # pyright: ignore[reportUnusedFunction]
    # this should never run
    raise AssertionError
