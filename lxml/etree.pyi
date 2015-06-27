# Minimal stubs for `lxml`, as needed by this project.
# A different incomplete set of stubs is shipped with my fork of `mypy`.

import typing

from typing import (
        Dict,
        Iterator,
)

class _Element:
    attrib = None # type: Dict[str, str]
    text = None # type: str

    def iterchildren(self, name: str) -> Iterator['_Element']:
        pass

class _ElementTree:
    def getroot(self) -> _Element:
        pass

class XMLSchema:
    def __init__(self, file: str) -> None:
        pass

class XMLParser:
    def __init__(self, schema: XMLSchema) -> None:
        pass

def parse(input: typing.BinaryIO, parser: XMLParser) -> _ElementTree:
    pass
