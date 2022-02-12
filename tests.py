"""
it runs some tests on the source code ranging from formatting
to type checking with mypy

"""


from pathlib import Path
import subprocess
import shlex
import black  # type: ignore[import]
import sys
import os

here = Path(os.path.abspath(__file__)).parent
all_scripts = [here / "corpe.py", here / "tests.py"]
all_scripts.extend(
    here / "src" / script
    for script in os.listdir(here / "src")
    if script.endswith(".py")
)
MyPy_SHOW_ERROR_CODES: bool = True


def echo_and_call(cmd: list[str]) -> None:
    print(f"[CMD] {shlex.join(cmd)}")
    subprocess.call(cmd)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-full")

    full = "-full" in sys.argv or "-f" in sys.argv

    if "-format" in sys.argv or full:
        for script in all_scripts:
            path = here / script
            if black.format_file_in_place(
                path, False, black.FileMode(), black.WriteBack.YES
            ):
                print(f"Formatted file: {script}")
            else:
                print(f"Skipping file {script} as it is already formatted")

    if "-mypy" in sys.argv or full:
        cmd = [sys.executable, "-m", "mypy"]
        cmd.extend(str(here / script) for script in all_scripts)
        if MyPy_SHOW_ERROR_CODES:
            cmd.append("--show-error-codes")
        echo_and_call(cmd)
