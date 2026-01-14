from pytest import mark


@mark.smoke
def test__smoke__cli_add(run_cli):
    actual_value = run_cli(["add", "4", "5"])
    assert "9.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_subtract(run_cli):
    actual_value = run_cli(["subtract", "10", "3"])
    assert "7.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_multiply(run_cli):
    actual_value = run_cli(["multiply", "6", "7"])
    assert "42.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_divide(run_cli):
    actual_value = run_cli(["divide", "10", "2"])
    assert "5.0" in actual_value.stdout


@mark.smoke
def test__smoke__cli_divide_by_zero(run_cli):
    actual_value = run_cli(["divide", "10", "0"])
    assert 1 == actual_value.returncode
    assert "Error: Cannot divide by zero." in actual_value.stderr


@mark.smoke
def test__smoke__cli_invalid_operation_error(run_cli):
    actual_value = run_cli(["mod", "5", "2"])
    assert 2 == actual_value.returncode
    assert ("error: argument operation: invalid choice: 'mod' (choose from 'add', 'subtract', 'multiply', 'divide')"
            in actual_value.stderr)


@mark.smoke
def test__smoke__cli_missing_arguments_error(run_cli):
    actual_value = run_cli(["add", "5"])
    assert 2 == actual_value.returncode
    assert "error: the following arguments are required: b" in actual_value.stderr
