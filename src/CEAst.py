from __future__ import annotations

from src.core import Patterns, CWD, BuildIn  # type: ignore[import]

from dataclasses import dataclass
from enum import auto, Enum

from pathlib import Path
from typing import *

import sys

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


class KeyWords(BuildIn, Enum):
    IF = auto()
    END = auto()
    WHILE = auto()
    DO = auto()
    CONST = auto()
    VAR = auto()
    SET = auto()
    MEM = auto()
    MEMSET = auto()
    MEMGET = auto()


class Types(BuildIn, Enum):
    INT = auto()


@dataclass
class Push(BuildIn):
    value: Union[str, int]
    typ: Types

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
    KeyWords.IF: "if",
    KeyWords.END: "end",
    KeyWords.WHILE: "while",
    KeyWords.DO: "do",
    KeyWords.CONST: "const",
    KeyWords.VAR: "var",
    KeyWords.SET: "set",
    KeyWords.MEM: "mem",
    KeyWords.MEMSET: "mem-set",
    KeyWords.MEMGET: "mem-get",
}


def run_checks():
    err: bool = False
    for team in [Intrinsics, KeyWords]:
        for op in team:
            if op not in mapping:
                print(f"{op} does not have a matching word", file=sys.stderr)
                err = True

    if err:
        sys.exit(1)


mapping_names: list[str] = list(mapping.values())


# Abstract Syntax Tree
@dataclass
class AST:
    path: Path
    body: list[BuildIn]
    variables: list[str]
    memories: list[Mem]


def parse_int(i: str) -> int:
    if Patterns.signed_integer.search(i) and i != "-":
        return int(i)
    if Patterns.signed_float.search(i) is not None:
        raise NotImplementedError("floating point numbers are not supported")
    raise ValueError(f"unable to interpret {repr(i)} as an integer")


def compiler_error(
    location: str, details: str, exit_code: int = 1, noexit: bool = False
) -> None:
    print(f"{location}: [ERROR]: {details}", file=sys.stderr)
    if not noexit:
        sys.exit(exit_code)


def format_location(file: str, line: int, column: int) -> str:
    return f"{file}:{line + 1}:{column + 1}"


@dataclass
class PushVariable(BuildIn):
    name: str

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class SetVariable(BuildIn):
    name: str

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class MemSet(BuildIn):
    name: str

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class MemGet(BuildIn):
    name: str

    def __eq__(self, other) -> bool:
        return type(self) == other


@dataclass
class Mem(BuildIn):
    size: int
    name: str


@dataclass
class Operation:
    loc: LocType
    word: str

    def format_location(self) -> str:
        return format_location(self.loc[0], self.loc[1], self.loc[2])


def corpe_basic_math_eval(ops: list[Operation], constants: dict[str, int]) -> int:
    stack = []
    for op in ops:
        if (
            Patterns.hexadecimal_format.search(op.word)
            or Patterns.binary_format.search(op.word)
            or isint(op.word)
        ):
            stack.append(eval(op.word, constants))
        elif op.word in constants:
            stack.append(constants[op.word])

        elif op.word == mapping[Intrinsics.ADD]:
            stack.append(int(stack.pop(-2) + stack.pop()))
        elif op.word == mapping[Intrinsics.SUB]:
            stack.append(int(stack.pop(-2) - stack.pop()))
        elif op.word == mapping[Intrinsics.DIV]:
            stack.append(int(stack.pop(-2) / stack.pop()))
        elif op.word == mapping[Intrinsics.MOD]:
            stack.append(int(stack.pop(-2) % stack.pop()))
        elif op.word == mapping[Intrinsics.MUL]:
            stack.append(int(stack.pop(-2) * stack.pop()))
        elif op.word == mapping[Intrinsics.POW]:
            stack.append(int(stack.pop(-2) ** stack.pop()))
        elif op.word == mapping[Intrinsics.BIN_AND]:
            stack.append(int(stack.pop(-2) & stack.pop()))
        elif op.word == mapping[Intrinsics.BIN_OR]:
            stack.append(int(stack.pop(-2) | stack.pop()))
        elif op.word == mapping[Intrinsics.BIN_INV]:
            stack.append(~stack.pop())
        elif op.word == mapping[Intrinsics.BIN_XOR]:
            stack.append(int(stack.pop(-2) ^ stack.pop()))
        elif op.word == mapping[Intrinsics.RSHIFT]:
            stack.append(int(stack.pop(-2) >> stack.pop()))
        elif op.word == mapping[Intrinsics.LSHIFT]:
            stack.append(int(stack.pop(-2) << stack.pop()))
        elif op.word == mapping[Intrinsics.LT]:
            stack.append(int(stack.pop(-2) < stack.pop()))
        elif op.word == mapping[Intrinsics.LE]:
            stack.append(int(stack.pop(-2) <= stack.pop()))
        elif op.word == mapping[Intrinsics.EQ]:
            stack.append(int(stack.pop(-2) == stack.pop()))
        elif op.word == mapping[Intrinsics.NE]:
            stack.append(int(stack.pop(-2) != stack.pop()))
        elif op.word == mapping[Intrinsics.GE]:
            stack.append(int(stack.pop(-2) >= stack.pop()))
        elif op.word == mapping[Intrinsics.GT]:
            stack.append(int(stack.pop(-2) > stack.pop()))
        else:
            raise NotImplementedError(
                f"'{op}' is not supported in the basic version of the eval"
            )

    return stack.pop()


def check_word_redefinition(name: str, constants: dict[str, int], variables: list[str], memories: list[Mem]) -> bool:
    if name in constants:
        return True
    if name in variables:
        return True
    if name in memories:
        return True
    return False


def isint(s: str) -> bool:
    try:
        return Patterns.signed_integer.findall(s)[0] == s and s != "-"
    except IndexError:
        return False


def makeAST(ops: list[tuple[LocType, str]]) -> AST:
    # NOTE: in C &var, were var is a pointer, it returns the address of it

    # all of the instructions that will be compiled
    body: list[BuildIn] = []
    # constants are only a parsing stage thing and not a compilation stage
    constants: dict[str, int] = {}
    # variables declared with the var keyword
    variables: list[str] = []
    # the arrays/memories declared with the mem keyword
    memories: list[Mem] = []

    # this is here so we can collect all of the errors that the program produces
    error_occurred: bool = False

    skips: int = 0

    ops_count: int = len(ops)

    # the operations that are to the right of the current operation
    ops_to_left: list[Operation]

    operations: list[Operation] = [Operation(x[0], x[1]) for x in ops]

    for i, op in enumerate(operations):
        ops_to_left = operations[i + 1 :]

        if skips:
            skips -= 1
            continue

        if op.word == mapping[KeyWords.CONST]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected name for constant definition but found nothing",
                    noexit=False,
                )
            elif len_ops_to_left == 1:
                compiler_error(
                    op.format_location(),
                    "a name, value and a ending was expected for a constant declaration",
                    noexit=False,
                )

            constant_name = ops_to_left[0].word
            if constant_name in mapping_names or constant_name in constants or constant_name in variables:
                compiler_error(
                    op.format_location(),
                    "can not redefine a already existing word",
                    noexit=False,
                )
            if Patterns.signed_integer.search(constant_name):
                compiler_error(
                    op.format_location(),
                    "constant name can not be a number",
                    noexit=False,
                )

            blocked = [
                mapping[KeyWords.IF],
                mapping[KeyWords.WHILE],
                mapping[KeyWords.DO],
                mapping[KeyWords.CONST],
                mapping[KeyWords.VAR],
                mapping[KeyWords.SET],
                mapping[KeyWords.MEM],
                mapping[KeyWords.MEMGET],
                mapping[KeyWords.MEMSET],
            ]

            cur_op_index = 1
            cur_op = ops_to_left[cur_op_index]
            operations_to_evaluate: list[Operation] = []
            skips += 1
            while cur_op.word != mapping[KeyWords.END]:
                skips += 1
                cur_op_index += 1
                if cur_op_index >= len_ops_to_left:
                    compiler_error(
                        op.format_location(),
                        "unable to find a end for the constant definition",
                        noexit=False,
                    )
                if cur_op.word in blocked:
                    compiler_error(
                        cur_op.format_location(),
                        f"{repr(cur_op.word)} is not allowed in constant definition",
                        noexit=False,
                    )
                operations_to_evaluate.append(cur_op)
                cur_op = ops_to_left[cur_op_index]
            skips += 1

            constants[constant_name] = corpe_basic_math_eval(
                operations_to_evaluate, constants
            )

        elif op.word == mapping[KeyWords.MEM]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected name for memory definition but found nothing",
                    noexit=False,
                )
            elif len_ops_to_left == 1:
                compiler_error(
                    op.format_location(),
                    "a name, value and a ending was expected for a memory declaration",
                    noexit=False,
                )

            mem_name = ops_to_left[0].word
            if check_word_redefinition(mem_name, constants, variables, memories):
                compiler_error(
                    op.format_location(),
                    "can not redefine a already existing word",
                    noexit=False,
                )

            if isint(mem_name):
                compiler_error(
                    op.format_location(),
                    "constant name can not be a number",
                    noexit=False,
                )

            blocked = [
                mapping[KeyWords.IF],
                mapping[KeyWords.WHILE],
                mapping[KeyWords.DO],
                mapping[KeyWords.CONST],
                mapping[KeyWords.VAR],
                mapping[KeyWords.SET],
                mapping[KeyWords.MEM],
                mapping[KeyWords.MEMGET],
                mapping[KeyWords.MEMSET],
            ]

            cur_op_index = 1
            cur_op = ops_to_left[cur_op_index]
            operations_to_evaluate: list[Operation] = []
            skips += 1
            while cur_op.word != mapping[KeyWords.END]:
                skips += 1
                cur_op_index += 1
                if cur_op_index >= len_ops_to_left:
                    compiler_error(
                        op.format_location(),
                        "unable to find a end for the memory definition",
                        noexit=False,
                    )
                if cur_op.word in blocked:
                    compiler_error(
                        cur_op.format_location(),
                        f"{repr(cur_op.word)} is not allowed in memory definition",
                        noexit=False,
                    )
                operations_to_evaluate.append(cur_op)
                cur_op = ops_to_left[cur_op_index]
            skips += 1

            memories.append(Mem(corpe_basic_math_eval(operations_to_evaluate, constants), mem_name))

        elif op.word == mapping[KeyWords.MEMSET]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected a name to set the value of a memory block",
                    noexit=False,
                )
            mem_name = ops_to_left[0].word

            if isint(mem_name):
                compiler_error(
                    ops_to_left[0].format_location(),
                    "expected a memory name but got an integer",
                    noexit=False
                )

            body.append(MemSet(mem_name))
            skips += 1
            continue

        elif op.word == mapping[KeyWords.MEMGET]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected a name to get the value of a memory block",
                    noexit=False,
                )
            mem_name = ops_to_left[0].word

            if isint(mem_name):
                compiler_error(
                    ops_to_left[0].format_location(),
                    "expected a memory name but got an integer",
                    noexit=False
                )

            body.append(MemGet(mem_name))
            skips += 1
            continue

        elif op.word == mapping[KeyWords.VAR]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected name for variable definition but found nothing",
                    noexit=False,
                )

            variable_name = ops_to_left[0].word
            if variable_name in mapping_names or variable_name in constants or variable_name in variables:
                compiler_error(
                    op.format_location(),
                    "can not redefine a already existing word",
                    noexit=False,
                )
            if Patterns.signed_integer.search(variable_name):
                compiler_error(
                    op.format_location(),
                    "variable name can not be a number",
                    noexit=False,
                )

            variables.append(variable_name)
            skips += 1
            continue

        elif op.word == mapping[KeyWords.SET]:
            len_ops_to_left = len(ops_to_left)
            if len_ops_to_left == 0:
                compiler_error(
                    op.format_location(),
                    "expected a name to set the value of a variable but found nothing",
                    noexit=False,
                )

            variable_name = ops_to_left[0].word

            if isint(variable_name):
                compiler_error(
                    ops_to_left[0].format_location(),
                    "expected a variable name but got an integer",
                    noexit=False
                )

            body.append(SetVariable(variable_name))
            skips += 1
            continue

        elif op.word in mapping_names:
            found = False
            for oper in mapping:
                if op.word == mapping[oper]:
                    body.append(oper)
                    found = True
                    break
                if found:
                    break
            if not found:
                raise NotImplementedError(op.word)

        elif (
            Patterns.hexadecimal_format.search(op.word)
            or Patterns.binary_format.search(op.word)
            or (
                Patterns.signed_integer.search(op.word) is not None
                and op.word != "-"
                and Patterns.signed_integer.findall(op.word)[0] == op.word
            )
        ):
            body.append(Push(eval(op.word), Types.INT))

        elif op.word in constants:
            body.append(Push(constants[op.word], Types.INT))

        elif op.word in variables:
            body.append(PushVariable(op.word))

        else:
            compiler_error(
                op.format_location(), f"unrecognised word {repr(op.word)}", noexit=True,
            )
            error_occurred = True

    if error_occurred:
        sys.exit(1)

    return AST(CWD, body, variables, memories)
