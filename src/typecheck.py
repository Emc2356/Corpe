# a script to do type checking
from __future__ import annotations

from src.core import Patterns, CWD, BuildIn  # type: ignore[import]
import src.IntRepr as CEAst  # type: ignore[import]

from typing import Optional

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

from collections import deque

import sys


DataStackType = deque[CEAst.Types]


def types_to_human(typs: list[CEAst.Types]) -> list[str]:
    return [typ_to_human(typ) for typ in typs]


def typ_to_human(typ: CEAst.Types) -> str:
    if typ == CEAst.Types.INT:
        return "int"
    if typ == CEAst.Types.POINTER:
        return "pointer"
    raise NotADirectoryError(typ)


def typecheck_error(
    location: str,
    details: str,
    node: Optional[BuildIn] = None,
    exitcode: int = 1,
    noexit: bool = False,
) -> None:
    print(f"{location}: ERROR: {details}")

    if node is not None:
        expanded_from = node.expanded_from
        while expanded_from is not None:
            typecheck_note(
                expanded_from.format_location(),
                f"expansion from {node.expanded_from.word}",
            )
            expanded_from = expanded_from.child
    if not noexit:
        sys.exit(exitcode)


def typecheck_node_expect_ptr_int_return_none(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 2:
        typecheck_error(
            node.format_location(),
            f"{name} expects one integer and one ptr on the stack but found {'one element in the stack' if len(stack) == 1 else 'no elements on the stack'}",
        )
    types = [stack[-1], stack[-2]]
    if types != [CEAst.Types.POINTER, CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected one pointer and one integer on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()
    stack.pop()


def typecheck_node_expect_ptr_return_int(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 1:
        typecheck_error(
            node.format_location(),
            f"{name} expects one integer and one ptr on the stack but found {'one element in the stack' if len(stack) == 1 else 'no elements on the stack'}",
        )
    types = [stack[-1]]
    if types != [CEAst.Types.POINTER]:
        typecheck_error(
            node.format_location(),
            f"{name} expected two integers on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()
    stack.append(Types.INT)


def typecheck_node_expect_two_ints_return_two_ints(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 2:
        typecheck_error(
            node.format_location(),
            f"{name} expects two integers on the stack but found {'one' if len(stack) == 1 else 'none'}",
        )
    types = [stack[-1], stack[-2]]
    if types != [CEAst.Types.INT, CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected two integers on top of the stack but found {types_to_human(types)}",
        )


def typecheck_node_expect_two_ints_return_one_int(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 2:
        typecheck_error(
            node.format_location(),
            f"{name} expects two integers on the stack but found {'one' if len(stack) == 1 else 'none'}",
        )
    types = [stack[-1], stack[-2]]
    if types != [CEAst.Types.INT, CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected two integers on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()


def typecheck_node_expect_two_ints_return_none(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 2:
        typecheck_error(
            node.format_location(),
            f"{name} expects two integers on the stack but found {'one' if len(stack) == 1 else 'none'}",
        )
    types = [stack[-1], stack[-2]]
    if types != [CEAst.Types.INT, CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected two integers on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()
    stack.pop()


def typecheck_node_expect_one_int_return_one_int(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 1:
        typecheck_error(
            node.format_location(),
            f"{name} expects one integer on the stack but found none",
        )
    types = [stack[-1]]
    if types != [CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected one integer on top of the stack but found {types_to_human(types)}",
        )


def typecheck_node_expect_one_int_return_none(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 1:
        typecheck_error(
            node.format_location(),
            f"{name} expects one integer on the stack but found none",
        )
    types = [stack[-1]]
    if types != [CEAst.Types.INT]:
        typecheck_error(
            node.format_location(),
            f"{name} expected one integer on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()


def typecheck_node_expect_one_ptr_return_none(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 1:
        typecheck_error(
            node.format_location(),
            f"{name} expects one integer on the stack but found none",
        )
    types = [stack[-1]]
    if types != [CEAst.Types.POINTER]:
        typecheck_error(
            node.format_location(),
            f"{name} expected one integer on top of the stack but found {types_to_human(types)}",
        )
    stack.pop()


def typecheck_node_must_have_two_elements(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 2:
        typecheck_error(
            node.format_location(),
            f"{name} expects at least two elements on the stack but found {'one' if len(stack) == 1 else 'none'}",
        )


def typecheck_node_must_have_one_element(
    stack: DataStackType, node: BuildIn, name: str
) -> None:
    if len(stack) < 1:
        typecheck_error(
            node.format_location(),
            f"{name} expects at least one element on the stack but found none",
        )


def typecheck_note(
    location: str, details: str, exitcode: int = 1, noexit: bool = False
) -> None:
    print(f"{location} NOTE: {details}")
    if not noexit:
        sys.exit(exitcode)


def stack_equality(stack1: DataStackType, stack2: DataStackType) -> bool:
    return list(stack1) == list(stack2)


def typecheck_AST(ast: CEAst.IntRepr) -> None:
    stack: DataStackType = deque()
    stacks: list[tuple[DataStackType, BuildIn]] = []

    for node in ast.body:
        if node == Push:
            stack.append(node.typ)
        elif node == PushMem:
            stack.append(Types.POINTER)
        elif node == Intrinsic:
            if node.typ == Intrinsics.ADD:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.ADD]
                )
            elif node.typ == Intrinsics.SUB:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.SUB]
                )
            elif node.typ == Intrinsics.DIV:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.DIV]
                )
            elif node.typ == Intrinsics.MOD:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.MOD]
                )
            elif node.typ == Intrinsics.MUL:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.MUL]
                )
            elif node.typ == Intrinsics.POW:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.POW]
                )
            elif node.typ == Intrinsics.BIN_AND:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.BIN_AND]
                )
            elif node.typ == Intrinsics.BIN_OR:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.BIN_OR]
                )
            elif node.typ == Intrinsics.BIN_INV:
                typecheck_node_expect_one_int_return_one_int(
                    stack, node, mapping[Intrinsics.BIN_INV]
                )
            elif node.typ == Intrinsics.BIN_XOR:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.BIN_XOR]
                )
            elif node.typ == Intrinsics.RSHIFT:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.RSHIFT]
                )
            elif node.typ == Intrinsics.LSHIFT:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.LSHIFT]
                )
            elif node.typ == Intrinsics.PRINT:
                typecheck_node_expect_one_int_return_none(
                    stack, node, mapping[Intrinsics.PRINT]
                )
            elif node.typ == Intrinsics.PUTC:
                typecheck_node_expect_one_int_return_none(
                    stack, node, mapping[Intrinsics.PUTC]
                )
            elif node.typ == Intrinsics.PUTSTR:
                typecheck_node_expect_one_ptr_return_none(
                    stack, node, mapping[Intrinsics.PUTSTR]
                )
            elif node.typ == Intrinsics.LT:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.LT]
                )
            elif node.typ == Intrinsics.LE:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.LE]
                )
            elif node.typ == Intrinsics.EQ:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.EQ]
                )
            elif node.typ == Intrinsics.NE:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.NE]
                )
            elif node.typ == Intrinsics.GE:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.GE]
                )
            elif node.typ == Intrinsics.GT:
                typecheck_node_expect_two_ints_return_one_int(
                    stack, node, mapping[Intrinsics.GT]
                )
            elif node.typ == Intrinsics.DROP:
                typecheck_node_must_have_one_element(
                    stack, node, mapping[Intrinsics.DROP]
                )
                stack.pop()
            elif node.typ == Intrinsics.DROP2:
                typecheck_node_must_have_two_elements(
                    stack, node, mapping[Intrinsics.DROP2]
                )
                stack.pop()
                stack.pop()
            elif node.typ == Intrinsics.DUP:
                typecheck_node_must_have_one_element(
                    stack, node, mapping[Intrinsics.DUP]
                )
                a = stack[-1]
                stack.append(a)
            elif node.typ == Intrinsics.DUP2:
                typecheck_node_must_have_one_element(
                    stack, node, mapping[Intrinsics.DUP2]
                )
                a = stack.pop()
                b = stack.pop()
                stack.append(a)
                stack.append(b)
                stack.append(a)
                stack.append(b)
            elif node.typ == Intrinsics.OVER:
                typecheck_node_must_have_two_elements(
                    stack, node, mapping[Intrinsics.OVER]
                )
                a = stack.pop()
                b = stack.pop()
                stack.append(b)
                stack.append(a)
                stack.append(b)
            elif node.typ == Intrinsics.SWAP:
                typecheck_node_must_have_two_elements(
                    stack, node, mapping[Intrinsics.SWAP]
                )
                a = stack.pop()
                b = stack.pop()
                stack.append(a)
                stack.append(b)
            elif node.typ == Intrinsics.CLEAR:
                stack.clear()
            elif node.typ == Intrinsics.DBG_PRINT_STACK:
                pass
            elif node.typ == Intrinsics.CAST_INT:
                if len(stack) < 1:
                    typecheck_error(
                        node.format_location(),
                        f"{mapping[Intrinsics.CAST_INT]} expected one element on the stack but found none",
                        node,
                    )
                stack.pop()
                stack.append(Types.INT)
            elif node.typ == Intrinsics.CAST_PTR:
                if len(stack) < 1:
                    typecheck_error(
                        node.format_location(),
                        f"{mapping[Intrinsics.CAST_PTR]} expected one element on the stack but found none",
                        node,
                    )
                stack.pop()
                stack.append(Types.POINTER)
            elif node.typ in {
                Intrinsics.STORE8,
                Intrinsics.STORE16,
                Intrinsics.STORE32,
                Intrinsics.STORE64,
            }:
                typecheck_node_expect_ptr_int_return_none(
                    stack, node, mapping[node.typ]
                )
            elif node.typ in {
                Intrinsics.LOAD8,
                Intrinsics.LOAD16,
                Intrinsics.LOAD32,
                Intrinsics.LOAD64,
            }:
                typecheck_node_expect_ptr_return_int(
                    stack, node, mapping[Intrinsics.LOAD8]
                )
            elif node.typ == Intrinsics.ARGC:
                stack.append(Types.INT)
            elif node.typ == Intrinsics.ARGV:
                stack.append(Types.POINTER)
            else:
                raise NotImplementedError(node)

        elif node == KeyWord:
            if node.typ == KeyWords.IF:
                stack.pop()
                stacks.append((stack, node))
                stack = stack.copy()
            elif node.typ == KeyWords.ELSE:
                if len(stacks) == 0:
                    typecheck_error(
                        node.format_location(),
                        "expected a 'if' before an else but found nothing"
                    )
                _expect, _op = stacks.pop()
                assert _op == KeyWord
                if _op.typ != KeyWords.IF:
                    typecheck_error(
                        node.format_location(),
                        f"expected a 'if' before an else but found `{mapping[_op.typ]}`"
                    )
                stacks.append((stack, node))
                stack = _expect
            elif node.typ == KeyWords.WHILE:
                stacks.append((stack, node))
                stack = stack.copy()
            elif node.typ == KeyWords.DO:
                expect, op = stacks.pop()
                if op.typ == KeyWords.WHILE:
                    stack.pop()
                    if not stack_equality(expect, stack):
                        typecheck_error(
                            op.format_location(),
                            f"can not change the data types in the data stack in while-do blocks",
                            node,
                            noexit=True,
                        )
                        typecheck_note(
                            op.format_location(),
                            f"\nexpected: {list(expect)}\n" f"got: {list(stack)}",
                        )
                    stacks.append((stack, node))
                    stack = stack.copy()
                else:
                    raise NotImplementedError(
                        f"{op} is not handled in typechecking with the DO keyword"
                    )
            elif node.typ == KeyWords.END:
                expect, op = stacks.pop()
                if op.typ == KeyWords.IF:
                    if not stack_equality(expect, stack):
                        typecheck_error(
                            op.format_location(),
                            f"can not change the data types in the data stack in if statements",
                            node,
                            noexit=True,
                        )
                        typecheck_note(
                            op.format_location(),
                            f"\nexpected: {list(expect)}\n" f"got: {list(stack)}",
                        )
                elif op.typ == KeyWords.ELSE:
                    if not stack_equality(expect, stack):
                        typecheck_error(
                            op.format_location(),
                            f"data types changed in the if branch need to be changed in the else branch",
                            node,
                            noexit=True,
                        )
                        typecheck_note(
                            op.format_location(),
                            f"\nexpected: {list(expect)}\n" f"got: {list(stack)}",
                        )
                elif op.typ == KeyWords.DO:
                    if not stack_equality(expect, stack):
                        typecheck_error(
                            op.format_location(),
                            f"can not change the data types in the data stack in do-end statements",
                            node,
                            noexit=True,
                        )
                        typecheck_note(
                            op.format_location(),
                            f"\nexpected: {list(expect)}\n" f"got: {list(stack)}",
                        )
                else:
                    raise NotImplementedError(node)
            else:
                raise NotImplementedError(node)
        else:
            raise NotImplementedError(node)

    if len(stack) != 0:
        typecheck_error(str(ast.path), f"unhandled data on the stack: {list(stack)}")
