from subprocess import run
from sys import executable
from pytest import fixture


@fixture
def run_cli():
    """Helper fixture to run CLI and capture output."""
    def _run(args):
        cli_arguments = [executable, "src/main.py"]
        cli_arguments.extend(args)
        result = run(
            cli_arguments,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result
    return _run
