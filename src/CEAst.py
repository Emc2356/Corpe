from __future__ import annotations

from src.core import (  # type: ignore[import]
    Patterns,
    CWD,
    BuildIn,
    Intrinsics,
    Intrinsic,
    KeyWords,
    KeyWord,
    mapping,
    mapping_names,
    Types,
    LocType,
    Push,
    Mem,
    PushMem,
)

from dataclasses import dataclass

from pathlib import Path
from typing import *

import sys


def run_checks():
    err: bool = False
    for team in [Intrinsics, KeyWords]:
        for op in team:
            if op not in mapping:
                print(f"{op} does not have a matching word", file=sys.stderr)
                err = True

    if err:
        sys.exit(1)


# Abstract Syntax Tree
@dataclass
class AST:
    path: Path
    body: list[BuildIn]
    memories: list[Mem]


def compiler_error(
    location: str, details: str, exit_code: int = 1, noexit: bool = False
) -> None:
    print(f"{location}: [ERROR]: {details}", file=sys.stderr)
    if not noexit:
        sys.exit(exit_code)


def format_location(file: str, line: int, column: int) -> str:
    return f"{file}:{line + 1}:{column + 1}"


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


def check_word_redefinition(
    name: str, constants: dict[str, int], memories: list[Mem]
) -> bool:
    if name in constants:
        return True
    if name in memories:
        return True
    return False


def isint(s: str) -> bool:
    try:
        return Patterns.signed_integer.findall(s)[0] == s and s != "-"
    except IndexError:
        return False


def can_be_int(s: str) -> bool:
    return (
        Patterns.hexadecimal_format.search(s)
        or Patterns.binary_format.search(s)
        or isint(s)
    )


def gather_ops_to_right_until_end(
    ops_to_right: list[Operation], blocked: list[str], out: list[Operation]
) -> int:
    """
    return codes:
        0: no errors
        1: operation was blocked (the operation that caused the error will be pushed to the output)
        2: end keyword was not found
    """
    for op in ops_to_right:
        if op.word in blocked:
            out.append(op)
            return 1
        if op.word == mapping[KeyWords.END]:
            return 0
        out.append(op)
    return 2


def makeAST(ops: list[tuple[LocType, str]], path: Path) -> AST:
    # NOTE: in C &var, were var is a pointer, it returns the address of it

    # all of the instructions that will be compiled
    body: list[BuildIn] = []
    # constants are only a parsing stage thing and not a compilation stage
    constants: dict[str, int] = {}
    # the arrays/memories declared with the mem keyword
    memories: list[Mem] = []
    memory_names: list[str] = []  # only at the make ast stage

    # this is here so we can collect all of the errors that the program produces
    error_occurred: bool = False

    skips: int = 0

    ops_count: int = len(ops)

    # the operations that are to the right of the current operation
    ops_to_left: list[Operation]

    operations: list[Operation] = [Operation(x[0], x[1]) for x in ops]

    for i, op in enumerate(operations):
        if skips:
            skips -= 1
            continue
        ops_to_left = operations[i + 1 :]

        if op.word == mapping[KeyWords.CONST]:
            blocked = [
                mapping[KeyWords.IF],
                mapping[KeyWords.WHILE],
                mapping[KeyWords.MEMORY],
                mapping[KeyWords.DO],
                mapping[KeyWords.CONST],
            ]

            operations_to_evaluate: list[Operation] = []
            ret_code = gather_ops_to_right_until_end(
                ops_to_left, blocked, operations_to_evaluate
            )
            skips += len(operations_to_evaluate) + 1

            if ret_code == 0:
                len_ops_to_left = len(ops_to_left)
                if len_ops_to_left == 0:
                    error_text = (
                        "expected name for constant definition but found nothing"
                    )
                if len_ops_to_left == 1:
                    error_text = "a name, value and a ending was expected for a constant declaration"
                if "error_text" in locals():
                    compiler_error(op.format_location(), error_text)
                constant_name = ops_to_left[0].word
                if check_word_redefinition(
                    constant_name, constants, memories
                ):
                    error_text = "can not redefine a already existing word"
                if can_be_int(constant_name):
                    error_text = "constant name can not be a number"
                if "error_text" in locals():
                    compiler_error(ops_to_left[0].format_location(), error_text)

                operations_to_evaluate = operations_to_evaluate[1:]
                if len(operations_to_evaluate) == 0:
                    compiler_error(
                        op.format_location(), f"constant declaration needs a body"
                    )

                constants[constant_name] = corpe_basic_math_eval(
                    operations_to_evaluate, constants
                )
                continue
            # anything from here is a error
            if ret_code == 1:
                compiler_error(
                    operations_to_evaluate[~0].word,
                    f"{operations_to_evaluate.pop().word} is not supported in a const declaration",
                )
            if ret_code == 2:
                compiler_error(
                    op.format_location(),
                    f"end for the const declaration was not found, const block needs to end with 'end' keyword",
                )

        elif op.word == mapping[KeyWords.MEMORY]:
            blocked = [
                mapping[KeyWords.IF],
                mapping[KeyWords.WHILE],
                mapping[KeyWords.MEMORY],
                mapping[KeyWords.DO],
                mapping[KeyWords.CONST],
            ]

            operations_to_evaluate = []
            ret_code = gather_ops_to_right_until_end(
                ops_to_left, blocked, operations_to_evaluate
            )
            skips += len(operations_to_evaluate) + 1

            if ret_code == 0:
                len_ops_to_left = len(ops_to_left)
                if len_ops_to_left == 0:
                    error_text = "expected name for memory definition but found nothing"
                if len_ops_to_left == 1:
                    error_text = "a name, value and a ending was expected for a memory declaration"
                if "error_text" in locals():
                    compiler_error(op.format_location(), error_text)
                mem_name = ops_to_left[0].word
                if check_word_redefinition(mem_name, constants, memories):
                    error_text = "can not redefine a already existing word"
                if can_be_int(mem_name):
                    error_text = "memory name can not be a number"
                if "error_text" in locals():
                    compiler_error(ops_to_left[0].format_location(), error_text)

                operations_to_evaluate = operations_to_evaluate[1:]
                if len(operations_to_evaluate) == 0:
                    compiler_error(
                        op.format_location(), f"memory declaration needs a body"
                    )

                memories.append(
                    Mem(
                        corpe_basic_math_eval(operations_to_evaluate, constants),
                        mem_name,
                        op.loc,
                    )
                )
                memory_names.append(mem_name)
                continue
            # anything from here is a error
            if ret_code == 1:
                compiler_error(
                    operations_to_evaluate[~0].word,
                    f"{operations_to_evaluate.pop().word} is not supported in a const declaration",
                )
            if ret_code == 2:
                compiler_error(
                    op.format_location(),
                    f"end for the const declaration was not found, const block needs to end with 'end' keyword",
                )

        elif op.word in memory_names:
            body.append(PushMem(op.word, op.loc))

        elif op.word in mapping_names:
            found = False
            for oper in Intrinsics:
                if op.word == mapping[oper]:
                    body.append(Intrinsic(oper, op.loc))
                    found = True
                    break
            for oper in KeyWords:
                if op.word == mapping[oper]:
                    body.append(KeyWord(oper, op.loc))
                    found = True
            if not found:
                raise NotImplementedError(op.word)

        elif can_be_int(op.word):
            # abuse bytecode optimization stage
            body.append(Push(eval(op.word), Types.INT))

        elif op.word in constants:
            body.append(Push(constants[op.word], Types.INT))

        elif op.word in variables:
            body.append(PushVariable(op.word, Types.INT))

        else:
            compiler_error(
                op.format_location(),
                f"unrecognised word {repr(op.word)}",
                noexit=True,
            )
            error_occurred = True

    if error_occurred:
        sys.exit(1)

    return AST(path, body, memories)
