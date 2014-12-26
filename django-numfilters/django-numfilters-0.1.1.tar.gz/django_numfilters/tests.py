import sys
import unittest
from decimal import Decimal

from templatetags import numfilters as nf

req_version = (3,)
cur_version = sys.version_info


class ConvertToNumberTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.number(1), 1)

    def test_negative(self):
        self.assertEqual(nf.number(-1), -1)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.number(long(1)), long(1))

    def test_float(self):
        self.assertEqual(nf.number(1.1), 1.1)

    def test_decimal(self):
        self.assertEqual(nf.number(Decimal('1.1')), Decimal('1.1'))

    def test_str_to_int(self):
        self.assertEqual(nf.number('1'), 1)

    def test_str_to_float(self):
        self.assertEqual(nf.number('1.1'), 1.1)


class AbsoluteValueTest(unittest.TestCase):
    def test_positive_int(self):
        self.assertEqual(nf.abs(1), 1)

    def test_negative_int(self):
        self.assertEqual(nf.abs(-1), 1)

    def test_positive_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.abs(long(1)), long(1))

    def test_negative_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.abs(long(-1)), long(1))

    def test_positive_float(self):
        self.assertEqual(nf.abs(float(1.1)), float(1.1))

    def test_negative_float(self):
        self.assertEqual(nf.abs(float(-1.1)), float(1.1))

    def test_positive_decimal(self):
        self.assertEqual(nf.abs(Decimal('1.1')), Decimal('1.1'))

    def test_negative_decimal(self):
        self.assertEqual(nf.abs(Decimal('-1.1')), Decimal('1.1'))

    def test_string(self):
        self.assertEqual(nf.abs('1'), 1)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.abs('a'), '')


class DivisionTest(unittest.TestCase):
    def test_int(self):
        if cur_version < req_version:
            self.assertEqual(nf.div(5, 2), 2)
        else:
            self.assertEqual(nf.div(5, 2), 2.5)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.div(long(5), long(2)), long(2))

    def test_float(self):
        self.assertEqual(nf.div(6.0, 2.5), 2.4)

    def test_decimal(self):
        self.assertEqual(nf.div(Decimal('6.0'), Decimal('2.0')), Decimal('3.0'))

    def test_string(self):
        self.assertEqual(nf.div('6', '2.5'), 2.4)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.div('1', 'a'), '')


class ExponentiationTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.pow(5, 2), 25)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.pow(long(5), long(2)), long(25))

    def test_float(self):
        self.assertEqual(nf.pow(5.0, 2.0), 25.0)

    def test_decimal(self):
        self.assertEqual(nf.pow(Decimal('5.0'), Decimal('2.0')), Decimal('25.0'))

    def test_string(self):
        self.assertEqual(nf.pow('5', '2'), 25)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.pow('1', 'a'), '')


class FloorDivisionTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.floordiv(5, 2), 2)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.floordiv(long(5), long(2)), long(2))

    def test_float(self):
        self.assertEqual(nf.floordiv(5.1, 2.1), 2.0)

    def test_decimal(self):
        self.assertEqual(nf.floordiv(Decimal('5.1'), Decimal('2.1')), Decimal('2.0'))

    def test_string(self):
        self.assertEqual(nf.floordiv('5', '2'), 2)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.floordiv('1', 'a'), '')


class ModuloTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.mod(5, 2), 1)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.mod(long(5), long(2)), long(1))

    def test_float(self):
        self.assertEqual(nf.mod(5.5, 2.5), 0.5)

    def test_decimal(self):
        self.assertEqual(nf.mod(Decimal('5.5'), Decimal('2.5')), Decimal('0.5'))

    def test_string(self):
        self.assertEqual(nf.mod(str(5.5), str(2.5)), 0.5)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.mod(str(5.5), 'a'), '')


class MultiplicationTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.mul(2, 3), 6)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.mul(long(2), long(3)), long(6))

    def test_float(self):
        self.assertEqual(nf.mul(2.5, 3.5), 8.75)

    def test_decimal(self):
        self.assertAlmostEqual(nf.mul(Decimal('2.5'), Decimal('3.5')), Decimal('8.75'), 2)

    def test_string(self):
        self.assertEqual(nf.mul(str(2.5), str(3.5)), 8.75)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.mul('1', 'a'), '')


class SquareRootTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.sqrt(4), 2)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.sqrt(long(4)), long(2))

    def test_float(self):
        self.assertEqual(nf.sqrt(4.0), 2.0)

    def test_decimal(self):
        self.assertEqual(nf.sqrt(Decimal('4.0')), 2.0)

    def test_string(self):
        self.assertEqual(nf.sqrt('4'), 2)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.sqrt(str('a')), '')


class SubtractionTest(unittest.TestCase):
    def test_int(self):
        self.assertEqual(nf.sub(1, 1), 0)

    def test_long(self):
        if cur_version < req_version:
            self.assertEqual(nf.sub(long(1), long(1)), long(0))

    def test_float(self):
        self.assertEqual(nf.sub(1.1, 1.1), 0)

    def test_decimal(self):
        self.assertEqual(nf.sub(Decimal('1.1'), Decimal('1.1')), Decimal('0'))

    def test_string(self):
        self.assertEqual(nf.sub('1', '1'), 0)

    def test_returns_empty_string_if_exception_is_raised(self):
        self.assertEqual(nf.sub('1', 'a'), '')


if __name__ == '__main__':
    unittest.main()