# `@main`.py

-----

[![PyPI version shields.io](https://img.shields.io/pypi/v/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)
[![PyPI license](https://img.shields.io/pypi/l/mainpy.svg)](https://pypi.python.org/pypi/mainpy/)

-----

## Basic Examples

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

If, for some reason, you cannot or don't want to use a decorator, you can also call the decorator with the function as an argument:

```python
import mainpy


def main(): ...


mainpy.main(main)
```

## External Libraries


### Click

With `click` you can simply add the decorator as usual, as long as you keep in mind that it has to be the first decorator (i.e. above the `@click.command()`):

```python
import click

import mainpy


@mainpy.main
@click.command()
def click_command():
    click.echo('Hello from click_command')
```

If you want to use `@click.group` you probably don't want to decorate the group because the decorator will immediately execute. In those cases you probably want to move the `mainpy.main(...)` execution to the bottom of the file:


```python
import click

import mainpy


@click.group()
def group(): ...
    

@group.command()
def command(): ...


mainpy.main(group)
```

### Typer

When using `typer` you also need to use the regular call instead of the decorator:

```python
import typer

import mainpy


app = typer.Typer()


@app.command()
def command():
    typer.echo('typer.Typer()')


mainpy.main(app)
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
