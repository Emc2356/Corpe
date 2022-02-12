from pathlib import Path
from enum import Enum
from typing import *

import re as regex

CWD: Path = Path().absolute()

COMMENT: str = "//"

EXTENSION: str = ".ce"

BOUNDS_CHECKING: bool = True

STACK_SIZE: int = 30000

INDENTATION: int = 2

_AbstractValue = TypeVar("_AbstractValue")


class Patterns:
    signed_integer = regex.compile(r"[-0-9]+")
    unsigned_integer = regex.compile(r"[0-9]+")
    signed_float = regex.compile(r"[-.0-9]+")
    unsigned_float = regex.compile(r"[.0-9]+")

    binary_format = regex.compile(r"0[bB][0-1]+")
    hexadecimal_format = regex.compile(r"0[xX][0-9a-fA-F]+")


# visual pleasing reasons
def abstract(obj: _AbstractValue) -> _AbstractValue:
    return obj


@abstract
class BuildIn:
    pass
