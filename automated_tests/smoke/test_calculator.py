from subprocess import run
from sys import executable
from pytest import mark


def run_cli(args):
    """Helper function to run CLI and capture output."""
    cli_arguments = [executable, "src/main.py"]
    cli_arguments.extend(args)
    result = run(
        cli_arguments,
        capture_output=True, text=True, timeout=5
    )
    return result


@mark.smoke
def test__smoke__cli_add():
    actual_value = run_cli(["add", "4", "5"])
    assert "9.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_subtract():
    actual_value = run_cli(["subtract", "10", "3"])
    assert "7.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_multiply():
    actual_value = run_cli(["multiply", "6", "7"])
    assert "42.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_divide():
    actual_value = run_cli(["divide", "10", "2"])
    assert "5.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_divide_by_zero():
    actual_value = run_cli(["divide", "10", "0"])
    assert 1 == actual_value.returncode
    assert "Error: Cannot divide by zero." in actual_value.stderr


@mark.smoke
def test__smoke__cli_invalid_operation_error():
    actual_value = run_cli(["mod", "5", "2"])
    assert 1 == actual_value.returncode
    assert ("error: argument operation: invalid choice: 'mod' (choose from add, subtract, multiply, divide)"
            in actual_value.stderr)


@mark.smoke
def test__smoke__cli_missing_arguments_error():
    actual_value = run_cli(["add", "5"])
    assert 2 == actual_value.returncode
    assert "error: the following arguments are required: b" in actual_value.stderr
