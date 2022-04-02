# `@main`.py

-----

[![PyPI version shields.io](https://img.shields.io/pypi/v/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)
[![PyPI license](https://img.shields.io/pypi/l/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)

-----

Instead of the verbose "boilerplate"

```python
def main(): ...

if __name__ == '__main__':
    main()
```

mainpy can be used to write it as:

```python
from mainpy import main

@main
def app(): ...
```

Similarly, the async boilerplate

```python
import asyncio

async def main(): ...

if __name__ == '__main__':
    asyncio.run(main())
```

can be replaced with

```python
@main
async def async_app(): ...
```


## Automatic uvloop usage

If you have [uvloop](https://github.com/MagicStack/uvloop) installed, mainpy
will automatically call `uvloop.install()` before running your async main 
function. This can be disabled by setting `use_uvloop=False`, e.g.:

```python
@main(use_uvloop=False)
async def app(): ...
```

## Debug mode

Optionally, python's [development mode](https://docs.python.org/3/library/devmode.html) 
can be emulated by setting `debug=True` in `@main`. This will enable the
[faulthandler](https://docs.python.org/3/library/faulthandler.html#faulthandler.enable), 
configure the [`warnings`](https://docs.python.org/3/library/warnings.html) 
filter to display all warnings, and activate the
[asyncio debug mode](https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode):

```python
@main(debug=True)
def app(): ...
```


## Installation

```bash
pip install mainpy
```

*requires python > 3.7*
