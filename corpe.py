# call the parsing module to create the operations
# create a Abstract-Syntax Tree (AST) from the operations
# generate the C code
# call a C compiler that will compile the generated C

from __future__ import annotations

from src.compiler import generate_c_code_from_AST  # type: ignore[import]

import subprocess
from pathlib import Path
from typing import Union
from src import core, parsing, IntRepr, typecheck  # type: ignore[import]
from typing import *
import functools
import shlex
import sys
import os


def read_file(filepath: Union[Path, str]) -> str:
    with open(filepath, "r") as f:
        return f.read()


def usage(program: str, target_file: TextIO = sys.stdout) -> None:
    put = functools.partial(print, file=target_file)
    put("[USAGE]")
    put(f"python {program} <subcommand> <file>")
    put("")
    put("subcommands:")
    put("    com <file> [options] (compile the program)")
    put(
        "        -r (run the generated file and the arguments that it has after it will be passed to that program)"
    )
    put("        -o [name] (modify the output file)")
    put("        -unsafe (no checks will happen)")
    put("    dump <file> [options] (dump the C code)")
    put("        -o [name] (modify the output file)")
    put("        -unsafe (no checks will happen)")
    put("    help (print this help message)")
    put("")


def echo_and_call(cmd: list[str]) -> int:
    print(f"[CMD] {shlex.join(cmd)}")
    return subprocess.call(cmd)


def main() -> None:

    assert len(sys.argv) >= 1, "How?"
    argv: list[str] = sys.argv[:]
    argc: int = len(argv)

    current_program_path: str
    subcommand: str

    current_program_path, *argv = argv

    if len(argv) < 1:
        usage(current_program_path, sys.stderr)
        sys.stderr.write("[ERROR]: no subcommand was provided\n")
        sys.exit(1)

    subcommand, *argv = argv

    if subcommand not in {"com", "dump", "help"}:
        usage(current_program_path, sys.stderr)
        sys.stderr.write(f"[ERROR]: {repr(subcommand)} is not a valid subcommand\n")
        sys.exit(1)

    if subcommand == "com":
        run: bool = False
        run_argv: list[str] = []
        unsafe: bool = False
        ce_file: Path
        c_file: Path
        executable_file: Path
        arg: str
        if len(sys.argv) == 0:
            usage(current_program_path, sys.stderr)
            sys.stderr.write("[ERROR]: no file was provided\n")
            sys.exit(1)
        ce_file = Path(argv.pop(0))
        c_file = (
            ce_file.parent / (".tempC." + ce_file.name[: -len(core.EXTENSION)] + ".c")
            if ce_file.name.endswith(core.EXTENSION)
            else ce_file.parent / (".tempC." + ce_file.name + ".c")
        )
        executable_file = (
            ce_file.parent / (ce_file.name[: -len(core.EXTENSION)] + ".exe")
            if ce_file.name.endswith(core.EXTENSION)
            else ce_file.parent / (ce_file.name + ".exe")
        )
        while len(argv):
            arg, *argv = argv
            if arg == "-unsafe":
                unsafe = True
            elif arg == "-o":
                if len(argv) == 0:
                    usage(current_program_path, sys.stderr)
                    sys.stderr.write("[ERROR]: no file was provided for the -o flag\n")
                    sys.exit(1)
                ce_file = Path(argv.pop(0))
                c_file = (
                    ce_file.parent / (".tempC." + ce_file.name[: -len(core.EXTENSION)] + ".c")
                    if ce_file.name.endswith(core.EXTENSION)
                    else ce_file.parent / (".tempC." + ce_file.name + ".c")
                )
                executable_file = (
                    ce_file.parent / (ce_file.name[: -len(core.EXTENSION)] + ".exe")
                    if ce_file.name.endswith(core.EXTENSION)
                    else ce_file.parent / (ce_file.name + ".exe")
                )
            elif arg == "-r":
                run_argv = argv[:]
                run = True
                break

        IntRepr.run_checks()

        with open(c_file, "w") as out:
            print(f"[INFO] parsing {ce_file}...")
            ast = IntRepr.makeAST(parsing.parse_file(str(ce_file)), Path(ce_file))
            if not unsafe:
                print(f"[INFO] type checking {ce_file}...")
                typecheck.typecheck_AST(ast)
            print("[INFO] generating C code...")
            out.write(generate_c_code_from_AST(ast, core.STACK_SIZE))

        print("[INFO] compiling with GCC compiler...")
        if echo_and_call(["gcc", str(c_file), "-o", str(executable_file)]):
            run = False
        print(f"[INFO] removing {c_file}...")
        os.remove(c_file)

        if run:
            print("[INFO] running the executable...")
            echo_and_call([str(executable_file), *run_argv])

    if subcommand == "dump":
        unsafe: bool = False  # type: ignore[no-redef]
        ce_file: Path  # type: ignore[no-redef]
        c_file: Path  # type: ignore[no-redef]
        arg: str  # type: ignore[no-redef]
        if len(sys.argv) == 0:
            usage(current_program_path, sys.stderr)
            sys.stderr.write("[ERROR]: no file was provided\n")
            sys.exit(1)
        ce_file = Path(argv.pop(0))
        c_file = (
            ce_file.parent / (ce_file.name[: -len(core.EXTENSION)] + ".c")
            if ce_file.name.endswith(core.EXTENSION)
            else ce_file.parent / (ce_file.name + ".c")
        )
        while len(argv):
            arg, *argv = argv
            if arg == "-unsafe":
                unsafe = True
            elif arg == "-o":
                if len(argv) == 0:
                    usage(current_program_path, sys.stderr)
                    sys.stderr.write("[ERROR]: no file was provided for the -o flag\n")
                    sys.exit(1)
                ce_file = Path(argv.pop(0))
                c_file = (
                    ce_file.parent / (ce_file.name[: -len(core.EXTENSION)] + ".c")
                    if ce_file.name.endswith(core.EXTENSION)
                    else ce_file.parent / (ce_file.name + ".c")
                )

        IntRepr.run_checks()

        with open(c_file, "w") as out:
            print(f"[INFO] parsing {ce_file}...")
            ast = IntRepr.makeAST(parsing.parse_file(str(ce_file)), Path(ce_file))
            if not unsafe:
                print(f"[INFO] type checking {ce_file}...")
                typecheck.typecheck_AST(ast)
            print("[INFO] generating C code...")
            out.write(generate_c_code_from_AST(ast, core.STACK_SIZE))

    if subcommand == "help":
        usage(current_program_path, sys.stdout)
        sys.exit(0)


if __name__ == "__main__":
    main()
