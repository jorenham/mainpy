"""Run as `python click_group.py app`."""

import click

import mainpy


@click.group()
def group() -> None: ...


@group.command()
def app() -> None:
    click.echo('Hello from `app()`')


mainpy.main(group)

print(f'{group = !r}')
print(f'{group.__module__ = !r}')
print(f'{group.callback = !r}')
print(f'{group.callback.__module__ = !r}')
