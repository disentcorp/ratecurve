import unittest
import numpy as np
import pandas as pd
import datetime
from dateroll import ddh, Duration
from ratecurve import Curve
from ratecurve.utils import *

Duration.just_bds = lambda self, *args,**kwargs: self.just_days

class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...
    
    def test_isdatelike(self):
        good_date = ddh('t')
        good_string = '1/1/2000'
        bad_string = 'apple'
        bad_type = 5
        self.assertEqual(isdatelike(good_date), True)
        self.assertEqual(isdatelike(good_string), True)
        self.assertEqual(isdatelike(bad_string), False)
        self.assertEqual(isdatelike(bad_type), False)

    def test_to_dateroll_date(self):
        good_date = ddh('t')
        bad_date = datetime.date.today()
        good_string_date = '1/1/2000'
        good_string_tenor = '3m'
        bad_string = 'apple'
        bad_type = 5
        #with base
        good_base = ddh('1/1/2000')
        bad_base = 'apple'
        to_dateroll_date(good_string_tenor,good_base)
        with self.assertRaises(Exception):
            to_dateroll_date(bad_date,good_base)
            to_dateroll_date(good_string_tenor,bad_base)
        #without base
        to_dateroll_date(good_date)
        with self.assertRaises(Exception):
            to_dateroll_date(good_string_tenor)
            to_dateroll_date(bad_string)
            to_dateroll_date(bad_type)


    def test_from_date_to_number(self):
        cal = "ALL"
        root = ddh('1/1/2000')
        good_date = ddh('t')
        bad_type = 5
        from_date_to_number(good_date, root, "ACT/365", cal)
        from_date_to_number(good_date, root, "bd/252", cal)
        with self.assertRaises(Exception):
            dc = "ACT/365"
            from_date_to_number(bad_type, root, dc, cal)
    
    def test_from_number_to_date(self):
        cal = "ALL"
        root = ddh('1/1/2000')
        number = 10
        dc = "ACT/365"
        from_number_to_date(number,root,dc, cal)
        
    def test_delta_t(self):
        date1 = ddh('t')
        date2 = ddh('t+5')
        dc = "ACT/365"
        cal = "ALL"
        delta_t(date1, date2, dc, cal)

if __name__ == "__main__":
    unittest.main()
