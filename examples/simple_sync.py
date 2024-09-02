from mainpy import main


@main
def app() -> int:
    print('Hello from `app()`')
    return 42


print('Result of `app()`:', repr(app))
