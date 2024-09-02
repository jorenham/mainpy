import click

import mainpy


@mainpy.main
@click.command()
def click_command() -> None:
    click.echo('Hello from `click_command()`')
