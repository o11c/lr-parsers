# Replacement stubs for `subprocess`,
# because the official ones use `IO[Any]` which prevents 100% coverage.

import typing

from typing import (
        List,
)

PIPE = -1

class Popen:
    stdin = None # type: typing.BinaryIO
    stdout = None # type: typing.BinaryIO

    def __init__(self, args: List[str], stdin: int, stdout: int) -> None:
        pass

    def wait(self) -> int:
        pass
