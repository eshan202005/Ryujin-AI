"""
Simple divide function.
"""

def divide(a, b):
    """Divide a by b and return the result.

    Raises ZeroDivisionError with a clear message if b == 0.
    """
    # Check for zero divisor explicitly to provide a clear error message
    try:
        if b == 0:
            raise ZeroDivisionError("division by zero: the divisor 'b' is zero")
    except TypeError:
        # If b cannot be compared to 0 (non-numeric), let the / operator raise the appropriate error
        pass
    return a / b
