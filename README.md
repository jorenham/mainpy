<h1 align="center"><code>@main</code>.py</h1>

<p align="center">
    <a href="https://pypi.org/project/mainpy/">
        <img
            alt="mainpy - PyPI"
            src="https://img.shields.io/pypi/v/mainpy?style=flat"
        />
    </a>
    <a href="https://github.com/jorenham/mainpy">
        <img
            alt="mainpy - Python Versions"
            src="https://img.shields.io/pypi/pyversions/mainpy?style=flat"
        />
    </a>
    <a href="https://github.com/jorenham/mainpy">
        <img
            alt="mainpy - license"
            src="https://img.shields.io/github/license/jorenham/mainpy?style=flat"
        />
    </a>
</p>
<p align="center">
    <a href="https://github.com/jorenham/mainpy/actions?query=workflow%3ACI">
        <img
            alt="mainpy - CI"
            src="https://github.com/jorenham/mainpy/workflows/CI/badge.svg"
        />
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img
            alt="mainpy - pre-commit"
            src="https://img.shields.io/badge/pre--commit-enabled-orange?logo=pre-commit"
        />
    </a>
    <!-- <a href="https://github.com/KotlinIsland/basedmypy">
        <img
            alt="mainpy - basedmypy"
            src="https://img.shields.io/badge/basedmypy-checked-fd9002"
        />
    </a> -->
    <a href="https://detachhead.github.io/basedpyright">
        <img
            alt="mainpy - basedpyright"
            src="https://img.shields.io/badge/basedpyright-checked-42b983"
        />
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img
            alt="mainpy - ruff"
            src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"
        />
    </a>
</p>

---

## Basic Examples

With `mainpy`, there's no need to write `if __name__ == '__main__'` the
boilerplate anymore:

<table>
<tr>
<th width="415px">without <code>mainpy</code></th>
<th width="415px">with <code>mainpy</code></th>
</tr>
<tr>
<td width="415px">

```python
if __name__ == '__main__':
    app()

def app(): ...
```

</td>
<td width="415px">

```python
from mainpy import main

@main
def app(): ...
```

</td>
</tr>
</table>

For async apps, the improvement becomes even more obvious:

<table>
<tr>
<th width="415px">without <code>mainpy</code></th>
<th width="415px">with <code>mainpy</code></th>
</tr>
<tr>
<td width="415px">

```python
import asyncio

async def async_app(): ...

if __name__ == '__main__':
    with asyncio.Runner() as runner:
        runner.run(async_app())
```

</td>
<td width="415px">

```python
from mainpy import main

@main
async def async_app(): ...
```

</td>
</tr>
</table>

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

The `mainpy` package is available on [pypi][PYPI] for Python $\ge 3.9$:

```shell
pip install mainpy
```

Additionally, you can install the [`uvloop`][UVLOOP] extra which will install
`uvloop>=0.15.2` (unless you're on windows):

```shell
pip install mainpy[uvloop]
```

[PYPI]: https://pypi.org/project/mainpy/
[UVLOOP]: https://github.com/MagicStack/uvloop
[CLICK]: https://github.com/pallets/click
[TYPER]: https://github.com/tiangolo/typer
[DEVMODE]: https://docs.python.org/3/library/devmode.html
[FAULTHANDLER]: https://docs.python.org/3/library/faulthandler.html
[WARNINGS]: https://docs.python.org/3/library/warnings.html
[ADEBUG]: https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode
