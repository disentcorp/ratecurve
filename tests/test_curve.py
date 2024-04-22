import unittest
import pandas as pd

from dateroll import ddh, Duration
from ratecurve import Curve

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
        test the data validation errors of curve
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
    
    def test_make_number_a_date(self):
        '''
        test number to date conversion
        '''
        curve_data =  {
        "0m":.053,    
        "1m":.0548,
        "30y":.0465}
        curve = Curve(curve_data)
        num = 1000
        curve.make_number_a_date(num)       

    def test_fit(self):
        '''
        test interpolation for various methods
        '''
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
        '''
        test callable class
        '''
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

    def test_fwd(self):
        '''
        test call for forward rate across various interpolation methods
        '''
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
    
    def test_spot(self):
        '''
        test spot function
        '''
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
