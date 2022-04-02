from __future__ import annotations

__all__ = ('main', )

import asyncio
import functools
import os
import sys

from typing import (
    Any,
    Awaitable,
    Callable,
    cast,
    Coroutine,
    overload,
    TypeVar,
    Union
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_T = TypeVar('_T')
_F = TypeVar('_F', bound=Callable)
_R = TypeVar('_R', bound=object)

_SCallable: TypeAlias = Union[Callable[..., _T], Callable[[], _T]]
_ACallable: TypeAlias = _SCallable[Awaitable[_R]]
_XCallable: TypeAlias = Union[_SCallable[_R], _ACallable[_R]]


def _infer_debug() -> bool:
    flags = sys.flags

    if flags.debug or flags.dev_mode:
        return True

    if '--debug' in sys.argv[1:]:
        return True

    env_debug = os.environ.get('DEBUG', '0')
    try:
        env_debug = int(env_debug)
    except ValueError:
        pass
    return bool(env_debug)


# noinspection PyPackageRequirements
def _infer_uvloop() -> bool:
    try:
        import uvloop
    except ImportError:
        return False
    else:
        return True


def _enable_debug():
    env = os.environ

    if not env.get('PYTHONWARNINGS'):
        import warnings
        warnings.simplefilter('always')

    if not (env.get('PYTHONDEVMODE') or env.get('PYTHONFAULTHANDLER')):
        import faulthandler
        faulthandler.enable()


# noinspection PyPackageRequirements,PyUnresolvedReferences
def main(
    function: _XCallable[_R] | None = None,
    *,
    debug: bool | None = None,
    is_async: bool | None = None,
    use_uvloop: bool | None = None,
) -> Union[Callable[[_XCallable[_R]], _R], _R]:
    if function is None:
        return cast(
            Callable[[_XCallable[_R]], _R],
            functools.partial(
                main,
                debug=debug,
                is_async=is_async,
                use_uvloop=use_uvloop
            )
        )

    if not callable(function):
        raise TypeError(f'expected a callable, got {type(function).__name__}')

    if function.__module__ != '__main__':
        return function

    if debug is None:
        debug = _infer_debug()

    if debug:
        _enable_debug()

    if is_async or is_async is None and asyncio.iscoroutinefunction(function):
        if use_uvloop or use_uvloop is None and _infer_uvloop():
            import uvloop
            uvloop.install()

        return asyncio.run(
            cast(Coroutine[Any, Any, _R], function()),
            debug=debug
        )

    else:
        return function()


@main
def __main():
    # this should never run
    assert False
