from pytest import mark, raises
from src.main import Calculator, main


@mark.unittest
def test__unittest__add_positive_numbers():
    assert Calculator.add(3, 5) == 8


@mark.unittest
def test__unittest__add_negative_numbers():
    assert Calculator.add(-3, -7) == -10


@mark.unittest
def test__unittest__add_mixed_sign():
    assert Calculator.add(-3, 7) == 4


@mark.unittest
def test__unittest__add_zero():
    assert Calculator.add(0, 10) == 10


@mark.unittest
def test__unittest__subtract_positive_numbers():
    assert Calculator.subtract(10, 3) == 7


@mark.unittest
def test__unittest__subtract_negative_numbers():
    assert Calculator.subtract(-5, -2) == -3


@mark.unittest
def test__unittest__subtract_to_zero():
    assert Calculator.subtract(4, 4) == 0


@mark.unittest
def test__unittest__subtract_mixed_sign():
    assert Calculator.subtract(4, -5) == 9


@mark.unittest
def test__unittest__multiply_positive_numbers():
    assert Calculator.multiply(4, 5) == 20


@mark.unittest
def test__unittest__multiply_negative_numbers():
    assert Calculator.multiply(-3, -6) == 18


@mark.unittest
def test__unittest__multiply_mixed_sign():
    assert Calculator.multiply(-4, 5) == -20


@mark.unittest
def test__unittest__multiply_by_zero():
    assert Calculator.multiply(10, 0) == 0


@mark.unittest
def test__unittest__divide_positive_numbers():
    assert Calculator.divide(10, 2) == 5


@mark.unittest
def test__unittest__divide_negative_numbers():
    assert Calculator.divide(-9, -3) == 3


@mark.unittest
def test__unittest__divide_mixed_sign():
    assert Calculator.divide(-8, 2) == -4


@mark.unittest
def test__unittest__divide_result_decimal():
    assert Calculator.divide(7, 2) == 3.5


@mark.unittest
def test__unittest__run_main_add():
    main(["add", "1", "1"])


@mark.unittest
def test__unittest__run_main_subtract():
    main(["subtract", "1", "1"])


@mark.unittest
def test__unittest__run_main_multiply():
    main(["multiply", "1", "1"])


@mark.unittest
def test__unittest__run_main_divide():
    main(["divide", "1", "1"])


@mark.unittest
def test__unittest__divide_by_zero():
    with raises(ValueError, match="Cannot divide by zero."):
        Calculator.divide(10, 0)
