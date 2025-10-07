import uuid
from typing import TYPE_CHECKING, cast

import pytest


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


# language=python
PY_SYNC = """
import mainpy

result = [None]

@mainpy.main
def sync_main():
    print({!r})
    result[0] = 42

assert result[0] == 42
""".strip()

# language=python
PY_ASYNC = """
import asyncio
import mainpy

result = [None]

@mainpy.main
async def async_main():
    print({!r})
    result[0] = await asyncio.sleep(1e-6, 42)

assert result[0] == 42
""".strip()


@pytest.mark.parametrize('template', [PY_SYNC, PY_ASYNC])
def test_output(pytester: pytest.Pytester, template: str) -> None:
    output_expect = uuid.uuid4().hex
    script = template.format(output_expect)

    fh = cast('Callable[[str], Path]', pytester.makepyfile)('test.py')
    _ = fh.write_text(script)

    result = pytester.runpython(fh)

    errors = result.stderr.str()
    assert not errors

    output = result.stdout.str()
    assert output.rstrip() == output_expect
