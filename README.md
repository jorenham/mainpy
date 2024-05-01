# `@main`.py

-----

[![mainpy - pypi version](https://img.shields.io/pypi/v/mainpy.svg)][PYPI]
[![mainpy - python versions](https://img.shields.io/pypi/pyversions/mainpy.svg)][PYPI]
[![mainpy - license](https://img.shields.io/pypi/l/mainpy.svg)][PYPI]
[![mainpy - workflow status](https://github.com/jorenham/mainpy/workflows/CI/badge.svg)][CI]
[![mainpy - basedpyright](https://img.shields.io/badge/basedpyright-checked-42b983)][BASEDPYRIGHT]
[![mainpy - ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][RUFF]

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

async def async_app(): ...

if __name__ == '__main__':
    with asyncio.Runner() as runner:
        runner.run(async_app())
```

can be replaced with

```python
from mainpy import main

@mainpy.main
async def async_app(): ...
```

If you cannot want to use a decorator, you can also call the decorator
with the function as an argument:

```python
def async_app(): ...

# do things before running async_app()

main(async_app)
```

## External Libraries

Even though `mainpy` requires no other dependencies than `typing_extensions`
(on Python < 3.10), it has optional support for [`uvloop`][UVLOOP], and plays
nicely with popular CLI libraries, e.g. [`click`][CLICK] and [`typer`][TYPER].

### `uvloop`

If you have [uvloop][UVLOOP] installed, mainpy will automatically call
`uvloop.install()` before running your async main function.
This can be disabled by setting `use_uvloop=False`, e.g.:

```python
@main(use_uvloop=False)
async def app(): ...
```

### Click

With [`click`][CLICK] you can simply add the decorator as usual.

> [!IMPORTANT]
> The `@mainpy.main` decorator must come *before* `@click.command()`.

```python
import mainpy
import click

@mainpy.main
@click.command()
def click_command():
    click.echo('Hello from click_command')
```

The function that is decorated with `@mainpy.main` is executed immediately.
But a `@click.group` must be defined *before* the command function.
In this case, `mainpy.main` should be called *after* all has been setup:

```python
import mainpy
import click

@click.group()
def group(): ...

@group.command()
def command(): ...

mainpy.main(group)
```

### Typer

A [`typer`][TYPER] internally does some initialization after a command
has been defined.
Instead of using `@mainpy.main` on the command itself, you should use
`mainpy.main()` manually:

```python
import mainpy
import typer

app = typer.Typer()

@app.command()
def command():
    typer.echo('typer.Typer()')

mainpy.main(command)
```

## Debug mode

Optionally, Python's [development mode][DEVMODE] can be emulated by passing
`debug=True` to `mainpy.main`. This does three things:

- Enable the [faulthandler][FAULTHANDLER]
- Configure [`warnings`][WARNINGS] to display all warnings
- Runs `async` functions in [debug mode][ADEBUG]

```python
@main(debug=True)
def app(): ...
```

## Installation

The `mainpy` package is available on [pypi][PYPI] for Python $\ge 3.8$:

```shell
pip install mainpy
```

Additionally, you can install the [`uvloop`][UVLOOP] extra which will install
`uvloop>=0.14` (unless you're on windows):

```shell
pip install mainpy[uvloop]
```

[PYPI]: https://pypi.org/project/mainpy/
[CI]: https://github.com/jorenham/mainpy/actions
[BASEDPYRIGHT]: https://detachhead.github.io/basedpyright/
[RUFF]: https://github.com/astral-sh/ruff
[UVLOOP]: https://github.com/MagicStack/uvloop
[CLICK]: https://github.com/pallets/click
[TYPER]: https://github.com/tiangolo/typer
[DEVMODE]: https://docs.python.org/3/library/devmode.html
[FAULTHANDLER]: https://docs.python.org/3/library/faulthandler.html
[WARNINGS]: https://docs.python.org/3/library/warnings.html
[ADEBUG]: https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode
