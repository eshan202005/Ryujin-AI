import unittest
from divide import divide

class TestDivide(unittest.TestCase):
    def test_integer_division(self):
        # dividing integers yields a float in Python 3
        self.assertEqual(divide(10, 2), 5.0)

    def test_float_division(self):
        self.assertAlmostEqual(divide(7.5, 2.5), 3.0)

    def test_negative_values(self):
        self.assertEqual(divide(-9, 3), -3.0)
        self.assertEqual(divide(9, -3), -3.0)

    def test_zero_numerator(self):
        self.assertEqual(divide(0, 5), 0.0)

    def test_zero_divisor(self):
        with self.assertRaises(ZeroDivisionError) as cm:
            divide(5, 0)
        # ensure the message is clear about divisor being zero
        self.assertIn("divisor", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
