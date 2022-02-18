from __future__ import annotations

from src.core import INDENTATION  # type: ignore[import]

import src.CEAst as CEAst  # type: ignore[import]

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

import textwrap

variable_prefix: str = "CeVariable_"
memory_prefix: str = "CeMemory_"
memory_padding: int = 100


def construct_name(name: str) -> str:
    """
    it takes in a string and it returns a series of numbers that corresponded to that name
    """
    return "".join(str(ord(char)) for char in name)


def generate_standard_code(
    out: list[str],
    ast: CEAst.AST,
    stack_size: int = 30000,
) -> None:
    # NOTE: indentation has to be 8 spaces

    push_mems: list[PushMem] = list(filter(lambda op: op == PushMem, ast.body))

    # to be sure that we dont access out of memory accidentally
    memories = "\n"
    memories += f"        int CEMemory[{memory_padding} + {sum(mem.size for mem in ast.memories)} + {memory_padding}];\n"
    for i, mem in enumerate(ast.memories):
        memories += f"        void* {memory_prefix}{i} = &CEMemory[{memory_padding + sum(mem.size for mem in ast.memories[:i])}]; // {mem.name}\n"
        mem.id = i
        for push_mem in push_mems:
            if push_mem.name == mem.name:
                push_mem.id = i

    string = textwrap.dedent(
        f"""
        #include <stdio.h>
        #include <stdlib.h>
        #include <math.h>
        
        int stack[{stack_size}];
        int stack_ptr = 0;
        {memories}
        void push(int value) {{
          stack[++stack_ptr] = value;
        }}
        
        int pop() {{
          return stack[stack_ptr--];
        }}
        
        void drop() {{
          stack_ptr -= 1;
        }}
        
        void drop2() {{
          stack_ptr -= 2;
        }}
        
        void dup() {{
          stack[++stack_ptr] = stack[stack_ptr - 1];
        }}
        
        void dup2() {{
          stack[++stack_ptr] = stack[stack_ptr - 1];
          stack[++stack_ptr] = stack[stack_ptr - 1];
        }}
        
        void swap() {{
          int temp = stack[stack_ptr];
          stack[stack_ptr] = stack[stack_ptr - 1];
          stack[stack_ptr - 1] = temp;
        }}
        
        void clear() {{
          stack_ptr = 0;
        }}
    """
    )
    out.extend(line + "\n" for line in string.splitlines())


def generate_c_code_from_AST(ast: CEAst.AST, stack_size: int = 30000) -> str:
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

    generate_standard_code(generated_standard_c, ast, stack_size)

    write("int main(int argc, char** argv) {")
    indentation_level += INDENTATION
    write("int a;")
    write("int b;")

    for op in ast.body:
        if op == Intrinsic:
            if op.typ == Intrinsics.ADD:
                write("// add")
                write("a = pop();")
                write("b = pop();")
                write("push(b + a);")
            elif op.typ == Intrinsics.SUB:
                write("// sub")
                write("a = pop();")
                write("b = pop();")
                write("push(b - a);")
            elif op.typ == Intrinsics.DIV:
                write("// div")
                write("a = pop();")
                write("b = pop();")
                write("push(b / a);")
            elif op.typ == Intrinsics.MOD:
                write("// mod")
                write("a = pop();")
                write("b = pop();")
                write("push(b % a);")
            elif op.typ == Intrinsics.MUL:
                write("// mul")
                write("a = pop();")
                write("b = pop();")
                write("push(b * a);")
            elif op.typ == Intrinsics.POW:
                write("// pow")
                write("a = pop();")
                write("b = pop();")
                write("push(pow(b, a));")
            elif op.typ == Intrinsics.BIN_AND:
                write("// bin and")
                write("a = pop();")
                write("b = pop();")
                write("push(b & a);")
            elif op.typ == Intrinsics.BIN_OR:
                write("// bin or")
                write("a = pop();")
                write("b = pop();")
                write("push(b | a);")
            elif op.typ == Intrinsics.BIN_INV:
                write("// bin inc")
                write("a = pop();")
                write("push(~a);")
            elif op.typ == Intrinsics.BIN_XOR:
                write("// bin xor")
                write("a = pop();")
                write("b = pop();")
                write("push(b ^ a);")
            elif op.typ == Intrinsics.RSHIFT:
                write("// bin right shift")
                write("a = pop();")
                write("b = pop();")
                write("push(b >> a);")
            elif op.typ == Intrinsics.LSHIFT:
                write("// bin left shift")
                write("a = pop();")
                write("b = pop();")
                write("push(b << a);")
            elif op.typ == Intrinsics.PRINT:
                write("// print")
                write('printf("%d\\n", pop());')
            elif op.typ == Intrinsics.PUTC:
                write("// putc")
                write("fputc((char) pop(), stdout);")
            elif op.typ == Intrinsics.LT:
                write("// less than")
                write("a = pop();")
                write("b = pop();")
                write("push(b < a);")
            elif op.typ == Intrinsics.LE:
                write("// less than or equal")
                write("a = pop();")
                write("b = pop();")
                write("push(b <= a);")
            elif op.typ == Intrinsics.EQ:
                write("// equal")
                write("a = pop();")
                write("b = pop();")
                write("push(b == a);")
            elif op.typ == Intrinsics.NE:
                write("// not equal")
                write("a = pop();")
                write("b = pop();")
                write("push(b != a);")
            elif op.typ == Intrinsics.GE:
                write("// greater than")
                write("a = pop();")
                write("b = pop();")
                write("push(b > a);")
            elif op.typ == Intrinsics.GT:
                write("// greater than or equal")
                write("a = pop();")
                write("b = pop();")
                write("push(b >= a);")
            elif op.typ == Intrinsics.DROP:
                write("// drop")
                write("drop();")
            elif op.typ == Intrinsics.DROP2:
                write("// 2drop")
                write("drop2();")
            elif op.typ == Intrinsics.DUP:
                write("// dup")
                write("dup();")
            elif op.typ == Intrinsics.DUP2:
                write("// 2dup")
                write("dup2();")
            elif op.typ == Intrinsics.SWAP:
                write("// swap")
                write("swap();")
            elif op.typ == Intrinsics.CLEAR:
                write("// clear stack")
                write("clear();")
            elif op.typ == Intrinsics.DBG_PRINT_STACK:
                write("for (int jj = 0; jj < stack_ptr; jj ++) {")
                write('  printf("%d:%d\\n", jj, stack[jj]);')
                write("}")
            elif op.typ == Intrinsics.CAST_PTR:  # ignore
                pass
            elif op.typ == Intrinsics.CAST_INT:  # ignore
                pass
            elif op.typ == Intrinsics.STORE8:
                write(f"((int*) pop())[0] = (char) pop();")
            elif op.typ == Intrinsics.LOAD8:
                write(f"push((char) ((int*) pop())[0]);")
            elif op.typ == Intrinsics.STORE16:
                write(f"((int*) pop())[0] = (short) pop();")
            elif op.typ == Intrinsics.LOAD16:
                write(f"push((short) ((int*) pop())[0]);")
            elif op.typ == Intrinsics.STORE32:
                write(f"((int*) pop())[0] = (int) pop();")
            elif op.typ == Intrinsics.LOAD32:
                write(f"push((long) ((int*) pop())[0]);")
            elif op.typ == Intrinsics.STORE64:
                write(f"((int*) pop())[0] = (long) pop();")
            elif op.typ == Intrinsics.LOAD64:
                write(f"push((long) ((int*) pop())[0]);")
            else:
                raise NotImplementedError(op)
        elif op == Push:
            # for mypy reasons
            assert isinstance(op, Push), "Is this even possible?"
            if op.typ == Types.INT:
                write(f"push({op.value});")
        elif op == KeyWord:
            if op.typ == KeyWords.IF:
                write("if (pop()) {")
                indentation_level += INDENTATION
            elif op.typ == KeyWords.END:
                indentation_level -= INDENTATION
                write("}")
            elif op.typ == KeyWords.WHILE:
                while_loop_count += 1
                write(f"while (_CeWhileLoopFunction{while_loop_count}()) ")

                while_loops.append(while_loop_count)
                indentation_levels.append(indentation_level)
                indentation_level = 0
                write(f"int _CeWhileLoopFunction{while_loop_count}() {{")
                indentation_level += INDENTATION
                write("int a, b;")
                # raise NotImplementedError(op)
            elif op.typ == KeyWords.DO:
                if while_loops:
                    write("return pop();")
                    indentation_level -= INDENTATION
                    write("}")
                    write("    ")
                    while_loops.pop()
                    indentation_level = indentation_levels.pop()
                write("{")
                indentation_level += INDENTATION
            elif op.typ == KeyWords.CONST:
                # no need to implement anything special for this as constants is a parsing stage thing
                continue
        elif op == PushMem:
            write(f"push((int) &{memory_prefix}{op.id});")
        else:
            raise NotImplementedError(op)

    indentation_level -= INDENTATION
    write("}")

    return (
        "".join(generated_standard_c)
        + "".join(generated_functions_c)
        + "".join(generated_c)
    )
