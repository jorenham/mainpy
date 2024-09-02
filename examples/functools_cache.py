from functools import lru_cache

from mainpy import main


@main
@lru_cache
def cached_app() -> float:
    print('Hello from `cached_app()`')
    return 22 / 7


print('Result of `cached_app()`:', repr(cached_app))
