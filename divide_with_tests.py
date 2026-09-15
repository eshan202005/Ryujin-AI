import unittest

def divide(a, b):
    """Return a divided by b.

    Raises:
        ValueError: if b is zero.
    """
    if b == 0:
        raise ValueError('division by zero')
    return a / b


class TestDivideFunction(unittest.TestCase):
    def test_int_division(self):
        self.assertEqual(divide(10, 2), 5)
        self.assertEqual(divide(-9, 3), -3)

    def test_float_division(self):
        self.assertAlmostEqual(divide(7.5, 2.5), 3.0)
        self.assertAlmostEqual(divide(1, 4), 0.25)

    def test_zero_numerator(self):
        self.assertEqual(divide(0, 5), 0)
        self.assertEqual(divide(0.0, 1.5), 0.0)

    def test_negative_values(self):
        self.assertEqual(divide(-10, 2), -5)
        self.assertEqual(divide(10, -2), -5)
        self.assertEqual(divide(-9, -3), 3)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError) as cm:
            divide(5, 0)
        self.assertEqual(str(cm.exception), 'division by zero')


if __name__ == '__main__':
    unittest.main()
