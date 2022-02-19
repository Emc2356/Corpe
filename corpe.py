# call the parsing module to create the operations
# create a Abstract-Syntax Tree (AST) from the operations
# generate the C code
# call a C compiler that will compile the generated C

from __future__ import annotations

from src.compiler import generate_c_code_from_AST  # type: ignore[import]

import subprocess
from pathlib import Path
from typing import Union
from src import core, parsing, CEAst, typecheck  # type: ignore[import]
import sys
import shlex


def read_file(filepath: Union[Path, str]) -> str:
    with open(filepath, "r") as f:
        return f.read()


def usage() -> None:
    print("[USAGE]")
    print("python corpe.py <FILEPATH>")
    print("Optional flags:")
    print("    -r (run the generated executable)")
    print("Compiler flags:")
    print("    -O0 (no optimizations, default)")
    print("    -O1 (some optimizations)")
    print("    -O2 (more optimizations)")
    print("    -O3 (even more optimizations)")
    print("    -Ofast (using experimental features)")
    sys.exit(1)


def consume_arg(arg: str) -> bool:
    if arg in sys.argv:
        sys.argv.remove(arg)
        return True
    return False


def get_optimization_flag() -> str:
    ret = "-O0"
    if consume_arg("-O0"):
        ret = "-O0"
    if consume_arg("-O1"):
        ret = "-O1"
    if consume_arg("-O2"):
        ret = "-O2"
    if consume_arg("-O3"):
        ret = "-O3"
    if consume_arg("-Ofast"):
        ret = "-Ofast"
    return ret


def echo_and_call(cmd: list[str]) -> int:
    print(f"[CMD] {shlex.join(cmd)}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 2 or any(
        x in sys.argv for x in ["-h", "--h", "-help", "--help"]
    ):
        usage()

    filepath: str = sys.argv.pop(1)
    base_filename: str = (
        filepath[: -len(core.EXTENSION)]
        if filepath.endswith(core.EXTENSION)
        else filepath
    )
    run: bool = "-r" in sys.argv

    optimization_flag: str = get_optimization_flag()

    CEAst.run_checks()

    with open(base_filename + ".c", "w") as out:
        print(f"[INFO] parsing {filepath}...")
        ast = CEAst.makeAST(parsing.parse_file(filepath), Path(filepath))
        print(f"[INFO] type checking {filepath}...")
        typecheck.typecheck_AST(ast)
        print("[INFO] generating C code...")
        out.write(generate_c_code_from_AST(ast, core.STACK_SIZE))

    print("[INFO] compiling with GCC compiler...")
    if echo_and_call(
        ["gcc", base_filename + ".c", "-o", base_filename + ".exe", optimization_flag]
    ):
        run = False

    if run:
        print("[INFO] running the executable...")
        echo_and_call([base_filename + ".exe"])
