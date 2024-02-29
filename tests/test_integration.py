# ruff: noqa: ERA001
import uuid

import pytest


# language=python
PY_SYNC = """
import mainpy

@mainpy.main
def sync_main():
    print({!r})
    return 42

assert sync_main == 42
""".strip()

# language=python
PY_ASYNC = """
import asyncio
import mainpy

@mainpy.main
async def async_main():
    print({!r})
    return await asyncio.sleep(1e-6, 42)

assert async_main == 42
""".strip()


@pytest.mark.parametrize('template', [PY_SYNC, PY_ASYNC])
def test_output(pytester: pytest.Pytester, template: str):
    output_expect = uuid.uuid4().hex
    script = template.format(output_expect)

    fh = pytester.makepyfile('test.py')  # pyright: ignore[reportUnknownMemberType]
    _ = fh.write_text(script)

    result = pytester.runpython(fh)

    errors = result.stderr.str()
    assert not errors

    output = result.stdout.str()
    assert output.rstrip() == output_expect
