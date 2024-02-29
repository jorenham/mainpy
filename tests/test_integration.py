import pytest


SCRIPT_CLICK_COMMAND = """
import click

import mainpy


@mainpy.main
@click.command()
def click_command():
    click.echo('click.command()')
"""

SCRIPT_CLICK_GROUP = """
import click

import mainpy


@click.group()
def click_group():
    click.echo('click.group()')


@click_group.command()
def click_group_command():
    click.echo('click.group().command()')


assert mainpy.main(click_group) is click_group
"""

OUTPUT_CLICK_GROUP = """
Usage: test_output.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  click-group-command
""".strip()


SCRIPT_TYPER = """
import typer

import mainpy


app = typer.Typer()


@app.command()
def typer_command():
    typer.echo('typer.Typer()')


assert mainpy.main(app) is app
"""

SCRIPT_DECORATOR = """
import mainpy


@mainpy.main
def regular_main():
    print('regular main call')
"""

SCRIPT_FUNCTION_CALL = """
import mainpy


def regular_main():
    print('mainpy.main()')
    return 123

assert mainpy.main(regular_main) == 123
"""


@pytest.mark.parametrize(
    ('script', 'output_expect'),
    [
        (SCRIPT_CLICK_COMMAND, 'click.command()'),
        (SCRIPT_CLICK_GROUP, OUTPUT_CLICK_GROUP),
        (SCRIPT_TYPER, 'typer.Typer()'),
        (SCRIPT_DECORATOR, 'regular main call'),
        (SCRIPT_FUNCTION_CALL, 'mainpy.main()'),
    ],
)
def test_output(
    pytester: pytest.Pytester,
    script: str,
    output_expect: str,
):
    fh = pytester.makepyfile('test.py')  # pyright: ignore[reportUnknownMemberType]
    _ = fh.write_text(script)

    result = pytester.runpython(fh)

    errors = result.stderr.str()
    assert not errors

    output = result.stdout.str()
    assert output == output_expect
