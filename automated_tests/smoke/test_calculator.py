# test_calculator.py

import pytest
from src.main import Calculator

# --- Addition Tests ---
def test_add_positive_numbers():
    assert Calculator.add(3, 5) == 8

def test_add_negative_numbers():
    assert Calculator.add(-3, -7) == -10

def test_add_mixed_sign():
    assert Calculator.add(-3, 7) == 4

def test_add_zero():
    assert Calculator.add(0, 10) == 10


# --- Subtraction Tests ---
def test_subtract_positive_numbers():
    assert Calculator.subtract(10, 3) == 7

def test_subtract_negative_numbers():
    assert Calculator.subtract(-5, -2) == -3

def test_subtract_to_zero():
    assert Calculator.subtract(4, 4) == 0


# --- Multiplication Tests ---
def test_multiply_positive_numbers():
    assert Calculator.multiply(4, 5) == 20

def test_multiply_negative_numbers():
    assert Calculator.multiply(-3, -6) == 18

def test_multiply_mixed_sign():
    assert Calculator.multiply(-4, 5) == -20

def test_multiply_by_zero():
    assert Calculator.multiply(10, 0) == 0


# --- Division Tests ---
def test_divide_positive_numbers():
    assert Calculator.divide(10, 2) == 5

def test_divide_negative_numbers():
    assert Calculator.divide(-9, -3) == 3

def test_divide_mixed_sign():
    assert Calculator.divide(-8, 2) == -4

def test_divide_result_decimal():
    assert Calculator.divide(7, 2) == 3.5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        Calculator.divide(10, 0)
