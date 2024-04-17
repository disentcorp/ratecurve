import unittest
import numpy as np
import pandas as pd

from dateroll import ddh, Duration
from ratecurve import Curve
from ratecurve.ratecurve import disc_factor,ln,e,convert_cap_factor_to_rate,cap_factor

Duration.just_bds = lambda self, *args,**kwargs: self.just_days

class TestCurve(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...

    def test_init(self):
        """
        test init
        """
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)

    def test_curve_data_validation(self):
        """
        test the data validation of curve
        """
        dict_curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "2m":.0551,
        "3m":.0545,
        "4m":.0544,
        "6m":.0538,
        "1y":.0517,
        "2y":.0493,
        "3y":.0477,
        "5y":.0461,
        "7y":.0460,
        "10y":.0456,
        "20y":.0477,
        "30y":.0465}

        series_curve_data = pd.Series(dict_curve_data)
        df_curve_data = pd.DataFrame(series_curve_data)
        df_curve_data_transpose = df_curve_data.T
        c1 = Curve(series_curve_data)
        c2 = Curve(df_curve_data)
        c3 = Curve(df_curve_data_transpose)

    def test_curve_bad_data_validation(self):
        """
        test the data validation of curve
        """
        bad_dict = {"1m":'apple'}
        bad_dimension_dataframe = pd.DataFrame({"A":[1,2,3],"B":[1,2,3]})
        bad_type_dataframe = pd.DataFrame({"A":[1,2,3]})
        with self.assertRaises(Exception):
            c1 = Curve(bad_dimension_dataframe)
        with self.assertRaises(Exception):
            c2 = Curve(bad_type_dataframe)
        with self.assertRaises(Exception):
            c3 = Curve(3)
        with self.assertRaises(Exception):
            c4 = Curve(bad_dict)


    def test_isdatelike(self):
        good_date = ddh('t')
        good_string = '1m'
        bad_string = 'apple'
        integer = 5

        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}

        curve = Curve(curve_data)

        self.assertEqual(curve.isdatelike(good_date),True)
        self.assertEqual(curve.isdatelike(good_string),True)
        self.assertEqual(curve.isdatelike(bad_string),False)
        self.assertEqual(curve.isdatelike(integer),False)

    def test_to_datelike(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)

        good_string = '1m'
        good_date = ddh('t')
        bad_schedule_string = 't,t+1m,1w'
        bad_string = 'apple'
        npdatetime = np.datetime64('2005-02-25')
        npdelta = np.timedelta64(1, 'D')
        num = 5

        to_datelike = curve.to_dateroll_date_like
        self.assertEqual(to_datelike(good_string),ddh(good_string))
        self.assertEqual(to_datelike(good_date),good_date)
        self.assertEqual(to_datelike(npdatetime),ddh(pd.Timestamp(npdatetime)))
        self.assertEqual(to_datelike(npdelta),ddh(pd.Timedelta(npdelta)))        

        with self.assertRaises(Exception):
            to_datelike(num)
        with self.assertRaises(Exception):
            to_datelike(bad_string)
        with self.assertRaises(Exception):
            to_datelike(bad_schedule_string)

    def test_to_dateroll_date(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)
        to_date = curve.to_dateroll_date

        dur = ddh('1m')
        date = ddh('t+1m')
        bad_string = 'apple'

        self.assertEqual(to_date(dur),curve.base + dur)
        self.assertEqual(to_date(date),date)
        with self.assertRaises(Exception):
            to_date(bad_string)

    def test_make_date_a_number(self):
        #TODO missing bd starts with thing
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)
        dc = curve.dc
        dc2 = "BD/252"
        cal = curve.cal

        date = ddh('t+1m')
        list_of_dates = ddh('t, t+1m,1d')
        list_of_dates_answer = [(d - '1/1/2000').just_days for d in list_of_dates]
        list_of_non_dates = [ 1,2,3]


        mdan = curve.make_date_a_number

        self.assertEqual(mdan(list_of_dates,dc,cal),list_of_dates_answer)
        self.assertEqual(mdan(date,dc,cal),(date - '1/1/2000').just_days)
        self.assertEqual(mdan(date,dc2,cal),(date - '1/1/2000').just_bds(cal=cal,dc=dc2))
        with self.assertRaises(Exception):
            mdan(list_of_non_dates,dc,cal)

    def test_make_number_a_date(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)
        dc = curve.dc
        cal = curve.cal
        mnad = curve.make_number_a_date

        date = ddh('t+1m')
        date_as_number = curve.make_date_a_number(date,dc,cal)
        self.assertEqual(mnad(date_as_number,cal),date)

    def test_disc_factor(self):
        method1 = "EXP"
        method2 = "YLD"
        method3 = "LIN"
        r = .05
        t = ddh('1y').just_days
        self.assertEqual(disc_factor(r,t,method1),1/(e**(r*t)))
        self.assertEqual(disc_factor(r,t,method2),1/((1+r)**t))
        self.assertEqual(disc_factor(r,t,method3),1/(1+r*t))
        with self.assertRaises(Exception):
            disc_factor(r,t,'apple'),1/(1+r*t)

    def test_fit(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        #test toy
        c1 = Curve(curve_data,interp_on = 'r')
        c2 = Curve(curve_data,interp_on = 'r*t')
        c3 = Curve(curve_data,interp_on = 'ln(df)')
        with self.assertRaises(Exception):
            c4 = Curve(curve_data,interp_on = 'apple')

    def test_call(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)

        d1 = ddh('t+6m')
        d2 = ddh('t+2y')

        curve(d1)
        curve(d1,d2)

        with self.assertRaises(Exception):
            curve(d1,d2,'apple')

    def test_cap_factor_to_rate(self):
        #also tests convert disc_factor_to_rate
        method1 = "EXP"
        method2 = "YLD"
        method3 = "LIN"
        cf = 1.05
        t = ddh('1y').just_days
        self.assertEqual(convert_cap_factor_to_rate(cf,t,method1),ln(cf)/t)
        self.assertEqual(convert_cap_factor_to_rate(cf,t,method2),(cf**(1/t)) - 1)
        self.assertEqual(convert_cap_factor_to_rate(cf,t,method3),(cf-1)/t)
        with self.assertRaises(Exception):
            convert_cap_factor_to_rate(cf,t,'apple')

    def test_cap_factor(self):
        #also tests convert disc_factor_to_rate
        method = "EXP"
        r = .05
        t = ddh('1y').just_days
        self.assertEqual(cap_factor(r,t,method),e**(r*t))      

    def test_fwd(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        c1 = Curve(curve_data,interp_on = 'r')
        c2 = Curve(curve_data,interp_on = 'r*t')
        c3 = Curve(curve_data,interp_on = 'ln(df)')

        #test from y 
        d1 = ddh('t+6m')
        d2 = ddh('t+2y') 
        
        #test from_y for various interp methods
        c1(d1,d2)
        c2(d1,d2)

        #test return settings
        c3.fwd(d1,d2,returns = 'df')
        with self.assertRaises(Exception):
            c3.fwd(d1,d2,returns='apple')
    
    def test_spot(self):
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data,)
        d1 = ddh('t+6m')
        curve.spot(d1)
        with self.assertRaises(Exception):
            curve.spot(d1,returns='apple')

if __name__ == "__main__":
    unittest.main()
