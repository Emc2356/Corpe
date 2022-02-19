from dataclasses import dataclass

from enum import Enum, auto
from pathlib import Path

from typing import *

import re as regex

CWD: Path = Path().absolute()

COMMENT: str = "//"

EXTENSION: str = ".ce"

STACK_SIZE: int = 30000

INDENTATION: int = 2

_AbstractValue = TypeVar("_AbstractValue")


class Patterns:
    signed_integer = regex.compile(r"^[-+]?\d+$")
    unsigned_integer = regex.compile(r"^([+-]?[1-9]\d*|0)$")
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


LocType = tuple[str, int, int]


class Intrinsics(BuildIn, Enum):
    ADD = auto()
    SUB = auto()
    DIV = auto()
    MOD = auto()
    MUL = auto()
    POW = auto()
    BIN_AND = auto()
    BIN_OR = auto()
    BIN_INV = auto()
    BIN_XOR = auto()
    RSHIFT = auto()
    LSHIFT = auto()
    PRINT = auto()
    PUTC = auto()
    LT = auto()
    LE = auto()
    EQ = auto()
    NE = auto()
    GE = auto()
    GT = auto()
    DROP = auto()
    DROP2 = auto()
    DUP = auto()
    DUP2 = auto()
    SWAP = auto()
    CLEAR = auto()
    DBG_PRINT_STACK = auto()
    CAST_INT = auto()
    CAST_PTR = auto()
    STORE8 = auto()
    LOAD8 = auto()
    STORE16 = auto()
    LOAD16 = auto()
    STORE32 = auto()
    LOAD32 = auto()
    STORE64 = auto()
    LOAD64 = auto()


class KeyWords(BuildIn, Enum):
    IF = auto()
    END = auto()
    WHILE = auto()
    MEMORY = auto()
    DO = auto()
    CONST = auto()
    MACRO = auto()
    ENDMACRO = auto()


class Types(BuildIn, Enum):
    INT = auto()
    POINTER = auto()


def format_location(file: str, line: int, column: int) -> str:
    return f"{file}:{line + 1}:{column + 1}"


@dataclass
class ExpandedFromNode:
    loc: LocType
    word: str
    child: Optional["ExpandedFromNode"] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])


@dataclass
class Push(BuildIn):
    value: Union[str, int]
    typ: Types
    expanded_from: Optional[str] = None

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class Intrinsic(BuildIn):
    typ: Intrinsics
    loc: LocType
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class KeyWord(BuildIn):
    typ: KeyWords
    loc: LocType
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class Operation:
    loc: LocType
    word: str
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])


@dataclass
class Macro(BuildIn):
    name: str
    loc: LocType
    ops: list[Operation]
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])


@dataclass
class Mem(BuildIn):
    size: int
    name: str
    loc: LocType
    id: int = -1  # will be set by the compiler.py file to simplify name
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class PushMem(BuildIn):
    name: str
    loc: LocType
    id: int = -1
    expanded_from: Optional[ExpandedFromNode] = None

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])

    def __eq__(self, other) -> bool:
        return type(self) == other


mapping: dict[BuildIn, str] = {
    Intrinsics.ADD: "+",
    Intrinsics.SUB: "-",
    Intrinsics.DIV: "/",
    Intrinsics.MOD: "%",
    Intrinsics.MUL: "*",
    Intrinsics.POW: "**",
    Intrinsics.BIN_AND: "&",
    Intrinsics.BIN_OR: "|",
    Intrinsics.BIN_INV: "~",
    Intrinsics.BIN_XOR: "^",
    Intrinsics.RSHIFT: ">>",
    Intrinsics.LSHIFT: "<<",
    Intrinsics.LT: "<",
    Intrinsics.LE: "<=",
    Intrinsics.EQ: "==",
    Intrinsics.NE: "!=",
    Intrinsics.GE: ">=",
    Intrinsics.GT: ">",
    Intrinsics.PRINT: "print",
    Intrinsics.PUTC: "putc",
    Intrinsics.DROP: "drop",
    Intrinsics.DROP2: "2drop",
    Intrinsics.DUP: "dup",
    Intrinsics.DUP2: "2dup",
    Intrinsics.SWAP: "swap",
    Intrinsics.CLEAR: "clear",
    Intrinsics.DBG_PRINT_STACK: "dbg-print-stack",
    Intrinsics.CAST_INT: "cast(int)",
    Intrinsics.CAST_PTR: "cast(ptr)",
    Intrinsics.STORE8: "!8",
    Intrinsics.LOAD8: "@8",
    Intrinsics.STORE16: "!16",
    Intrinsics.LOAD16: "@16",
    Intrinsics.STORE32: "!32",
    Intrinsics.LOAD32: "@32",
    Intrinsics.STORE64: "!64",
    Intrinsics.LOAD64: "@64",
    KeyWords.IF: "if",
    KeyWords.END: "end",
    KeyWords.WHILE: "while",
    KeyWords.DO: "do",
    KeyWords.CONST: "const",
    KeyWords.MEMORY: "memory",
    KeyWords.MACRO: "macro",
    KeyWords.ENDMACRO: "endmacro",
}
mapping_names: list[str] = list(mapping.values())
