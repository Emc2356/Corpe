from __future__ import annotations

from src.core import INDENTATION  # type: ignore[import]

import src.CEAst as CEAst  # type: ignore[import]

Intrinsics = CEAst.Intrinsics
KeyWords = CEAst.KeyWords
Push = CEAst.Push
PushVariable = CEAst.PushVariable
Types = CEAst.Types
SetVariable = CEAst.SetVariable
Mem = CEAst.Mem
MemSet = CEAst.MemSet
MemGet = CEAst.MemGet

variable_prefix: str = "_CeVariable_"
memory_prefix: str = "_CeMemory_"


def construct_name(name: str) -> str:
    """
    it takes in a string and it returns a series of numbers that cresponsed to that name
    """
    return "".join(str(ord(char)) for char in name)


def generate_standard_code(
    out: list[str],
    ast: CEAst.AST,
    do_bounds_checking: bool = False,
    stack_size: int = 30000,
) -> None:
    indentation_level: int = 0

    def write(s: str) -> None:
        if s != "":
            out.append(f"{' ' * indentation_level}{s}\n")
        elif s == "    ":
            out.append("\n")

    # TODO: when we implement static type checking we can remove the bounds checking
    def generate_bounds_checking_code() -> str:
        if do_bounds_checking:
            padding = " " * indentation_level + " " * INDENTATION
            return (
                # the first line is auto-indented by the write function
                f"if (stack_ptr >= {stack_size} || stack_ptr < 0) {{\n"
                f'{padding}printf("index %d went out of range %d", stack_ptr, {stack_size});\n'
                f"{padding}exit(1);\n"
                f"{' ' * indentation_level}}}"
            )
        return ""

    write("#include <stdio.h>")
    write("#include <stdlib.h>")
    write("#include <math.h>")
    write("    ")
    write(f"int stack[{stack_size}];")
    write("int stack_ptr = 0;")
    write("    ")
    for name in ast.variables:
        write(f"int {variable_prefix}{construct_name(name)};")
    write("    ")
    for mem in ast.memories:
        write(f"int {memory_prefix}{construct_name(mem.name)}[{mem.size}];")
    write("    ")
    write("void push(int value) {")
    indentation_level += INDENTATION
    write("stack_ptr += 1;")
    write(generate_bounds_checking_code())
    write("stack[stack_ptr] = value;")
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("int pop() {")
    indentation_level += INDENTATION
    write("int value = stack[stack_ptr];")
    write("stack_ptr -= 1;")
    write(generate_bounds_checking_code())
    write("return value;")
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void drop() {")
    indentation_level += INDENTATION
    write("stack_ptr -= 1;")
    write(generate_bounds_checking_code())
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void drop2() {")
    indentation_level += INDENTATION
    write("stack_ptr -= 2;")
    write(generate_bounds_checking_code())
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void dup() {")
    indentation_level += INDENTATION
    write("stack_ptr += 1;")
    write(generate_bounds_checking_code())
    write("stack[stack_ptr] = stack[stack_ptr - 1];")
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void dup2() {")
    indentation_level += INDENTATION
    write("stack_ptr += 1;")
    write(generate_bounds_checking_code())
    write("stack[stack_ptr] = stack[stack_ptr - 1];")
    write("stack_ptr += 1;")
    write(generate_bounds_checking_code())
    write("stack[stack_ptr] = stack[stack_ptr - 1];")
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void swap() {")
    indentation_level += INDENTATION
    write("int temp = stack[stack_ptr];")
    write("stack_ptr -= 1;")
    write(generate_bounds_checking_code())
    write("stack_ptr += 1;")
    write("stack[stack_ptr] = stack[stack_ptr - 1];")
    write("stack[stack_ptr - 1] = temp;")
    indentation_level -= INDENTATION
    write("}")
    write("    ")
    write("void clear() {")
    indentation_level += INDENTATION
    write("stack_ptr = 0;")
    indentation_level -= INDENTATION
    write("}")
    write("    ")


def generate_c_code_from_AST(
    ast: CEAst.AST, do_bounds_checking: bool = False, stack_size: int = 30000
) -> str:
    generated_c: list[str] = []
    generated_functions_c: list[str] = []
    generated_standard_c: list[str] = []

    indentation_level: int = 0
    indentation_levels: list[int] = []

    while_loops: list[int] = []
    while_loop_count: int = -1

    def write(s: str, end: str = "\n") -> None:
        if while_loops:
            if s != "":
                generated_functions_c.append(f"{' ' * indentation_level}{s}{end}")
        elif s != "":
            generated_c.append(f"{' ' * indentation_level}{s}{end}")

    generate_standard_code(
        generated_standard_c, ast, do_bounds_checking, stack_size
    )

    write("int main(int argc, char** argv) {")
    indentation_level += INDENTATION
    write("int a;")
    write("int b;")

    for op in ast.body:
        if op == Intrinsics.ADD:
            write("// add")
            write("a = pop();")
            write("b = pop();")
            write("push(b + a);")
        elif op == Intrinsics.SUB:
            write("// sub")
            write("a = pop();")
            write("b = pop();")
            write("push(b - a);")
        elif op == Intrinsics.DIV:
            write("// div")
            write("a = pop();")
            write("b = pop();")
            write("push(b / a);")
        elif op == Intrinsics.MOD:
            write("// mod")
            write("a = pop();")
            write("b = pop();")
            write("push(b % a);")
        elif op == Intrinsics.MUL:
            write("// mul")
            write("a = pop();")
            write("b = pop();")
            write("push(b * a);")
        elif op == Intrinsics.POW:
            write("// pow")
            write("a = pop();")
            write("b = pop();")
            write("push(pow(b, a));")
        elif op == Intrinsics.BIN_AND:
            write("// bin and")
            write("a = pop();")
            write("b = pop();")
            write("push(b & a);")
        elif op == Intrinsics.BIN_OR:
            write("// bin or")
            write("a = pop();")
            write("b = pop();")
            write("push(b | a);")
        elif op == Intrinsics.BIN_INV:
            write("// bin inc")
            write("a = pop();")
            write("push(~a);")
        elif op == Intrinsics.BIN_XOR:
            write("// bin xor")
            write("a = pop();")
            write("b = pop();")
            write("push(b ^ a);")
        elif op == Intrinsics.RSHIFT:
            write("// bin right shift")
            write("a = pop();")
            write("b = pop();")
            write("push(b >> a);")
        elif op == Intrinsics.LSHIFT:
            write("// bin left shift")
            write("a = pop();")
            write("b = pop();")
            write("push(b << a);")
        elif op == Intrinsics.PRINT:
            write("// print")
            write('printf("%d\\n", pop());')
        elif op == Intrinsics.PUTC:
            write("// putc")
            write("fputc((char) pop(), stdout);")
        elif op == Intrinsics.LT:
            write("// less than")
            write("a = pop();")
            write("b = pop();")
            write("push(b < a);")
        elif op == Intrinsics.LE:
            write("// less than or equal")
            write("a = pop();")
            write("b = pop();")
            write("push(b <= a);")
        elif op == Intrinsics.EQ:
            write("// equal")
            write("a = pop();")
            write("b = pop();")
            write("push(b == a);")
        elif op == Intrinsics.NE:
            write("// not equal")
            write("a = pop();")
            write("b = pop();")
            write("push(b != a);")
        elif op == Intrinsics.GE:
            write("// greater than")
            write("a = pop();")
            write("b = pop();")
            write("push(b > a);")
        elif op == Intrinsics.GT:
            write("// greater than or equal")
            write("a = pop();")
            write("b = pop();")
            write("push(b >= a);")
        elif op == Intrinsics.DROP:
            write("// drop")
            write("drop();")
        elif op == Intrinsics.DROP2:
            write("// 2drop")
            write("drop2();")
        elif op == Intrinsics.DUP:
            write("// dup")
            write("dup();")
        elif op == Intrinsics.DUP2:
            write("// 2dup")
            write("dup2();")
        elif op == Intrinsics.SWAP:
            write("// swap")
            write("swap();")
        elif op == Intrinsics.CLEAR:
            write("// clear stack")
            write("clear();")
        elif op == Push:
            # for mypy reasons
            assert type(op) == Push, "Is this even possible?"
            if op.typ == Types.INT:
                write(f"push({op.value});")
        elif op == KeyWords.IF:
            write("if (pop()) {")
            indentation_level += INDENTATION
        elif op == KeyWords.END:
            indentation_level -= INDENTATION
            write("}")
        elif op == KeyWords.WHILE:
            while_loop_count += 1
            write(f"while (_CeWhileLoopFunction{while_loop_count}()) ")

            while_loops.append(while_loop_count)
            indentation_levels.append(indentation_level)
            indentation_level = 0
            write(f"int _CeWhileLoopFunction{while_loop_count}() {{")
            indentation_level += INDENTATION
            write("int a, b;")
            # raise NotImplementedError(op)
        elif op == KeyWords.DO:
            if while_loops:
                write("return pop();")
                indentation_level -= INDENTATION
                write("}")
                write("    ")
                while_loops.pop()
                indentation_level = indentation_levels.pop()
            write("{")
            indentation_level += INDENTATION
        elif op == KeyWords.CONST:
            # no need to implement anything special for this as constants is a parsing stage thing
            continue
        elif op == PushVariable:
            write(f"push({variable_prefix}{construct_name(op.name)});")
        elif op == SetVariable:
            write(f"{variable_prefix}{construct_name(op.name)} = pop();")
        elif op == Intrinsics.DBG_PRINT_STACK:
            write("for (int jj = 0; jj < stack_ptr; jj ++) {")
            write("  printf(\"%d:%d\\n\", jj, stack[jj]);")
            write("}")
        elif op == MemSet:
            name = op.name
            write("if (stack_ptr < 2) {")
            write("  printf(\"expected at least 2 elements on top of the stack to set memory\\n\");")
            write("  exit(1);")
            write("}")
            write(f"{memory_prefix}{construct_name(name)}[pop()] = pop();")
        elif op == MemGet:
            name = op.name
            write("if (stack_ptr < 1) {")
            write("  printf(\"expected at least 1 element on top of the stack to get a part from the memory\\n\");")
            write("  exit(1);")
            write("}")
            write(f"push({memory_prefix}{construct_name(name)}[pop()]);")
        else:
            raise NotImplementedError(op)

    indentation_level -= INDENTATION
    write("}")

    return (
        "".join(generated_standard_c)
        + "".join(generated_functions_c)
        + "".join(generated_c)
    )
