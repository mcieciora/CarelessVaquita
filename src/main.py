import argparse
import sys


class Calculator:
    """
    A simple calculator supporting basic arithmetic operations.

    All methods are static, so they can be called directly without
    creating an instance of the class.
    """

    @staticmethod
    def add(a, b):
        """Return the sum of two numbers."""
        return a + b

    @staticmethod
    def subtract(a, b):
        """Return the difference between two numbers."""
        return a - b

    @staticmethod
    def multiply(a, b):
        """Return the product of two numbers."""
        return a * b

    @staticmethod
    def divide(a, b):
        """
        Return the quotient of dividing `a` by `b`.

        Raises:
            ValueError: If `b` is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b


def main(argv=None):
    """
    Command-line interface for the Calculator.

    Example:
        $ python calculator.py add 4 5
        Result: 9
    """
    parser = argparse.ArgumentParser(description="Simple CLI calculator")
    parser.add_argument("operation", choices=["add", "subtract", "multiply", "divide"],
                        help="Arithmetic operation to perform")
    parser.add_argument("a", type=float, help="First number")
    parser.add_argument("b", type=float, help="Second number")

    args = parser.parse_args(argv)

    try:
        if args.operation == "add":
            result = Calculator.add(args.a, args.b)
        elif args.operation == "subtract":
            result = Calculator.subtract(args.a, args.b)
        elif args.operation == "multiply":
            result = Calculator.multiply(args.a, args.b)
        elif args.operation == "divide":
            result = Calculator.divide(args.a, args.b)
        else:
            parser.error("Unknown operation")

        print(f"Result: {result}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
