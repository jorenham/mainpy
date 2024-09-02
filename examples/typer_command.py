import typer

import mainpy


app = typer.Typer()


@app.command()
def command() -> None:
    typer.echo('typer.Typer()')


mainpy.main(command)
