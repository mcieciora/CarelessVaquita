# test_calculator_cli.py

import pytest
from src.main import main


def run_cli(args, capsys):
    """Helper function to run CLI and capture output."""
    with pytest.raises(SystemExit) as e:
        main(args)
    return e.value.code, capsys.readouterr()


# --- Valid operations ---
def test_cli_add(capsys):
    exit_code, out = run_cli(["add", "4", "5"], capsys)
    assert exit_code == 0 or exit_code is None
    assert "Result: 9.0" in out.out

def test_cli_subtract(capsys):
    exit_code, out = run_cli(["subtract", "10", "3"], capsys)
    assert "Result: 7.0" in out.out

def test_cli_multiply(capsys):
    exit_code, out = run_cli(["multiply", "6", "7"], capsys)
    assert "Result: 42.0" in out.out

def test_cli_divide(capsys):
    exit_code, out = run_cli(["divide", "10", "2"], capsys)
    assert "Result: 5.0" in out.out


# --- Error handling ---
def test_cli_divide_by_zero(capsys):
    exit_code, out = run_cli(["divide", "10", "0"], capsys)
    assert exit_code == 1
    assert "Error: Cannot divide by zero." in out.err

def test_cli_invalid_operation(capsys):
    with pytest.raises(SystemExit):
        main(["mod", "5", "2"])  # argparse will exit on invalid choice


# --- CLI argument validation ---
def test_cli_missing_arguments(capsys):
    with pytest.raises(SystemExit):
        main(["add", "5"])  # missing one argument
