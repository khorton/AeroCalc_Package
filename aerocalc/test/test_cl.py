#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Test cases for cl module.
Run this script directly to do all the tests.
"""

# Done    1. 29 Jun 2009 - Ran 2to3 tool and fixed errors

# 0.20  28 Feb 2020  Python 3 compatibility

import unittest
import sys

# sys.path.append('/Users/kwh/python/')

sys.path.append('../')

import cl


def RE(value, truth):
    """ Return the absolute value of the relative error.
    """

    return abs((value - truth) / truth)


class Test_eas2cl(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.eas2cl(
            50,
            1800,
            110,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            )
        Truth = 1.9333626157
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.eas2cl(
            115,
            700,
            8.5,
            weight_units='kg',
            area_units='m**2',
            speed_units='mph',
            )
        Truth = 0.49889058073
        self.assertTrue(RE(Value, Truth) <= 1e-5)


class Test_cas2cl(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.cas2cl(
            200,
            20000,
            2000,
            100,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            alt_units='ft',
            )
        Truth = 0.15149332672
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.cas2cl(
            80,
            4500,
            700,
            8.5,
            weight_units='kg',
            area_units='m**2',
            speed_units='km/h',
            alt_units='m',
            )
        Truth = 2.6721923079
        self.assertTrue(RE(Value, Truth) <= 1e-5)


class Test_tas2cl(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.tas2cl(
            80,
            20000,
            2000,
            100,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            alt_units='ft',
            )
        Truth = 1.73241190
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.tas2cl(
            80,
            10000,
            2250,
            200,
            200,
            temp_units='K',
            weight_units='kg',
            area_units='m**2',
            speed_units='m/s',
            alt_units='m',
            )
        Truth = 0.07487161
        self.assertTrue(RE(Value, Truth) <= 1e-5)


class Test_cl2eas(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.cl2eas(
            0.41956654,
            1000,
            110,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            )
        Truth = 80
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.cl2eas(
            0.11254822,
            800,
            10,
            weight_units='kg',
            area_units='m**2',
            speed_units='ft/s',
            )
        Truth = 350
        self.assertTrue(RE(Value, Truth) <= 1e-5)


class Test_cl2cas(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.cl2cas(
            0.15149332672,
            20000,
            2000,
            100,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            alt_units='ft',
            )
        Truth = 200
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.cl2cas(
            2.6721923079,
            4500,
            700,
            8.5,
            weight_units='kg',
            area_units='m**2',
            speed_units='km/h',
            alt_units='m',
            )
        Truth = 80
        self.assertTrue(RE(Value, Truth) <= 1e-5)


class Test_cl2tas(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.cl2tas(
            1.73241190,
            20000,
            2000,
            100,
            weight_units='lb',
            area_units='ft**2',
            speed_units='kt',
            alt_units='ft',
            )
        Truth = 80
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.cl2tas(
            0.07487161,
            10000,
            2250,
            200,
            200,
            temp_units='K',
            weight_units='kg',
            area_units='m**2',
            speed_units='m/s',
            alt_units='m',
            )
        Truth = 80
        self.assertTrue(RE(Value, Truth) <= 1e-5)

class Test_cl2lift(unittest.TestCase):

    """All truth values hand calculated using a spreadsheet program, using a 
    different approach to correcting for altitude and temperature and using
    ConvertAll for unit conversions.
    """

    def test_01(self):

        Value = cl.cl2lift(
            0.41956654,
            80,
            110,
            lift_units='lb',
            area_units='ft**2',
            speed_units='kt',
            )
        Truth = 1000
        self.assertTrue(RE(Value, Truth) <= 1e-5)

    def test_02(self):

        Value = cl.cl2lift(
            0.11254822,
            350,
            10,
            lift_units='kg',
            area_units='m**2',
            speed_units='ft/s',
            )
        Truth = 800
        self.assertTrue(RE(Value, Truth) <= 1e-5)

# create test suites

main_suite = unittest.TestSuite()
suite1 = unittest.makeSuite(Test_eas2cl)
suite2 = unittest.makeSuite(Test_cas2cl)
suite3 = unittest.makeSuite(Test_tas2cl)
suite4 = unittest.makeSuite(Test_cl2eas)
suite5 = unittest.makeSuite(Test_cl2cas)
suite6 = unittest.makeSuite(Test_cl2tas)
suite7 = unittest.makeSuite(Test_cl2lift)
# add test suites to main test suite, so all test results are in one block

main_suite.addTest(suite1)
main_suite.addTest(suite2)
main_suite.addTest(suite3)
main_suite.addTest(suite4)
main_suite.addTest(suite5)
main_suite.addTest(suite6)
main_suite.addTest(suite7)
# main_suite.addTest(suite8)
# main_suite.addTest(suite9)
# main_suite.addTest(suite10)
# main_suite.addTest(suite11)
# main_suite.addTest(suite12)

# run main test suite
# if we run the main test suite, we get a line for each test, plus any
# tracebacks from failures.

unittest.TextTestRunner(verbosity=5).run(main_suite)

# if we run unittest.main(), we get just a single line of output, plus any
# tracebacks from failures.
# if __name__ == '__main__':
#     unittest.main()

