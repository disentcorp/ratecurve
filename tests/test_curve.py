import unittest

import pandas as pd
from dateroll import Duration, ddh
from ratecurve import Curve

Duration.just_bds = lambda self, *args, **kwargs: self.just_days


class TestCurve(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...

    def test_init(self):
        """
        test init
        """
        curve_data = {"0m": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(curve_data)
        self.assertEqual(curve.raw_data, curve_data)

    def test_curve_data_validation(self):
        """
        test the data validation of curve
        """
        dict_curve_data = {
            "1d": 0.053,
            "1m": 0.0548,
            "2m": 0.0551,
            "3m": 0.0545,
            "4m": 0.0544,
            "6m": 0.0538,
            "1y": 0.0517,
            "2y": 0.0493,
            "3y": 0.0477,
            "5y": 0.0461,
            "7y": 0.0460,
            "10y": 0.0456,
            "20y": 0.0477,
            "30y": 0.0465,
        }

        series_curve_data = pd.Series(dict_curve_data)
        df_curve_data = pd.DataFrame(series_curve_data)
        df_curve_data_transpose = df_curve_data.T
        c1 = Curve(series_curve_data)
        self.assertEqual(c1.raw_data, dict_curve_data)
        c2 = Curve(df_curve_data)
        self.assertEqual(c2.raw_data, dict_curve_data)
        c3 = Curve(df_curve_data_transpose)
        self.assertEqual(c3.raw_data, dict_curve_data)

    def test_curve_bad_data_validation(self):
        """
        test the data validation errors of curve
        """
        bad_dict = {"1m": "apple"}
        bad_dimension_dataframe = pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]})
        bad_type_dataframe = pd.DataFrame({"A": [1, 2, 3]})
        with self.assertRaises(Exception):
            c1 = Curve(bad_dimension_dataframe)
        with self.assertRaises(Exception):
            c2 = Curve(bad_type_dataframe)
        with self.assertRaises(Exception):
            c3 = Curve(3)
        with self.assertRaises(Exception):
            c4 = Curve(bad_dict)

    def test_make_number_a_date(self):
        """
        test number to date conversion
        """
        curve_data = {"1d": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(curve_data)
        num = 1000
        curve.make_number_a_date(num)

    def test_fit(self):
        """
        test interpolation for various methods
        """
        curve_data = {"1d": 0.053, "1m": 0.0548, "30y": 0.0465}
        # test toy
        c1 = Curve(curve_data, interp_on="r")
        c1.spot("0d")
        self.assertAlmostEqual(c1.spot("1d"), 0.053)
        self.assertAlmostEqual(c1.spot("1m"), 0.0548)
        self.assertAlmostEqual(c1.spot("30y"), 0.0465)

        c2 = Curve(curve_data, interp_on="r*t")
        c2.spot("0d")
        self.assertAlmostEqual(c2.spot("1d"), 0.053)
        self.assertAlmostEqual(c2.spot("1m"), 0.0548)
        self.assertAlmostEqual(c2.spot("30y"), 0.0465)
        c3 = Curve(curve_data, interp_on="ln(df)")
        c3.spot("0d")
        self.assertAlmostEqual(c3.spot("1d"), 0.053)
        self.assertAlmostEqual(c3.spot("1m"), 0.0548)
        self.assertAlmostEqual(c3.spot("30y"), 0.0465)
        with self.assertRaises(Exception):
            c4 = Curve(curve_data, interp_on="apple")
        with self.assertRaises(Exception):
            c5 = Curve(curve_data, extrap_method="apple")

    def test_call(self):
        """
        test callable class
        """
        curve_data = {"1d": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(curve_data)

        d1 = ddh("t+6m")
        d2 = ddh("t+2y")

        curve(d1)
        curve(d1, d2)

        with self.assertRaises(Exception):
            curve(d1, d2, "apple")

    def test_fwd(self):
        """
        test call for forward rate across various interpolation methods
        """
        curve_data = {"1d": 0.053, "1m": 0.0548, "30y": 0.0465}
        c1 = Curve(curve_data, interp_on="r")
        c2 = Curve(curve_data, interp_on="r*t")
        c3 = Curve(curve_data, interp_on="ln(df)")

        # test from y
        d1 = ddh("t+6m")
        d2 = ddh("t+2y")

        # test from_y for various interp methods
        c1(d1, d2)
        c2(d1, d2)
        c3(d1, d2)

    def test_spot(self):
        """
        test spot function
        """
        curve_data = {"1d": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(
            curve_data,
        )
        d1 = ddh("t+6m")
        curve.spot(d1)
        with self.assertRaises(Exception):
            curve.spot(d1, returns="apple")

    def test_extrapolated_spot_flat(self):
        """
        test spot function on extrapolated dates. test across interpolation methods, extrapolation methods and both forward and backwards interpolation
        """
        curve_data = {"5d": 0.053, "1m": 0.0548, "30y": 0.0465}
        d1 = ddh("t+1d")
        d2 = ddh("t+31y")
        # Test across interp_on
        c1 = Curve(curve_data, interp_on="r*t")
        self.assertAlmostEqual(c1.spot(d1), 0.053)  # Floating point errors occur
        self.assertAlmostEqual(c1.spot(d2), 0.0465)
        c2 = Curve(curve_data)
        self.assertAlmostEqual(c2.spot(d1), 0.053)
        self.assertAlmostEqual(c2.spot(d2), 0.0465)
        c3 = Curve(curve_data, interp_on="r")
        self.assertAlmostEqual(c3.spot(d1), 0.053)
        self.assertAlmostEqual(c3.spot(d2), 0.0465)

    def test_extrapolated_spot_extrapolate(self):
        """
        test spot function on extrapolated dates. test across interpolation methods, extrapolation methods and both forward and backwards interpolation
        """
        curve_data = {"5d": 0.053, "1m": 0.0548, "30y": 0.0465}
        d1 = ddh("t+1d")
        d2 = ddh("t+31y")
        # Test across interp_on
        c1 = Curve(curve_data, interp_on="r", extrap_method="extrapolate")
        self.assertLess(c1.spot(d1), 0.053)
        self.assertLess(c1.spot(d2), 0.0465)
        c2 = Curve(curve_data, interp_on="r*t", extrap_method="extrapolate")
        self.assertLess(c2.spot(d1), 0.053)
        self.assertLess(c2.spot(d2), 0.0465)
        c3 = Curve(curve_data, extrap_method="extrapolate")
        self.assertLess(c3.spot(d1), 0.053)
        self.assertLess(c3.spot(d2), 0.0465)

    def test_extrapolated_fwd_flat(self):
        """
        test fwd function on extrapolated dates with flat extrapolation setting.
        test across two front extraps, two back extraps and all permutations.
        """
        curve_data = {"5d": 0.053, "1m": 0.0548, "30y": 0.0465}
        dlow1 = ddh("t+1d")
        dlow2 = ddh("t+2d")
        d = ddh("t+1y")
        dhigh1 = ddh("t+31y")
        dhigh2 = ddh("t+35y")
        ###extrap method = 'flat'
        c1 = Curve(curve_data, interp_on="r*t")
        # Two low dates
        self.assertAlmostEqual(c1.fwd(dlow1, dlow2), 0.053)
        # Two high dates
        self.assertAlmostEqual(c1.fwd(dhigh1, dhigh2), 0.0465)
        # Low and high date
        c1.fwd(dlow1, dhigh1)
        # Low and middle date
        c1.fwd(dlow1, d)
        # Middle and high date
        c1.fwd(d, dhigh1)

        c2 = Curve(curve_data)
        # Two low dates
        self.assertAlmostEqual(c2.fwd(dlow1, dlow2), 0.053)
        # Two high dates
        self.assertAlmostEqual(c2.fwd(dhigh1, dhigh2), 0.0465)
        # Low and high date
        c2.fwd(dlow1, dhigh1)
        # Low and middle date
        c2.fwd(dlow1, d)
        # Middle and high date
        c2.fwd(d, dhigh1)

        c3 = Curve(curve_data, interp_on="r")
        # Two low dates
        self.assertAlmostEqual(c3.fwd(dlow1, dlow2), 0.053)
        # Two high dates
        self.assertAlmostEqual(c3.fwd(dhigh1, dhigh2), 0.0465)
        # Low and high date
        c3.fwd(dlow1, dhigh1)
        # Low and middle date
        c3.fwd(dlow1, d)
        # Middle and high date
        c3.fwd(d, dhigh1)

    def test_extrapolated_fwd_extrapolate(self):
        """
        test fwd function on extrapolated dates with extrapolation ends setting.
        test across two front extraps, two back extraps and all permutations.
        """
        curve_data = {"5d": 0.053, "1m": 0.0548, "30y": 0.0465}
        dlow1 = ddh("t+1d")
        dlow2 = ddh("t+2d")
        d = ddh("t+1y")
        dhigh1 = ddh("t+31y")
        dhigh2 = ddh("t+35y")

        c1 = Curve(curve_data, interp_on="r", extrap_method="extrapolate")
        # Two low dates
        self.assertLess(c1.fwd(dlow1, dlow2), 0.053)
        # Two high dates
        self.assertLess(c1.fwd(dhigh1, dhigh2), 0.0465)
        # Low and high date
        c1.fwd(dlow1, dhigh1)
        # Low and middle date
        c1.fwd(dlow1, d)
        # Middle and high date
        c1.fwd(d, dhigh1)

        c2 = Curve(curve_data, interp_on="r*t", extrap_method="extrapolate")
        # Two low dates
        c2.fwd(dlow1, dlow2)
        # Two high dates
        c2.fwd(dhigh1, dhigh2)
        # Low and high date
        c2.fwd(dlow1, dhigh1)
        # Low and middle date
        c2.fwd(dlow1, d)
        # Middle and high date
        c2.fwd(d, dhigh1)
        
        c3 = Curve(curve_data, extrap_method="extrapolate")
        # Two low dates
        c3.fwd(dlow1, dlow2)
        # Two high dates
        c3.fwd(dhigh1, dhigh2)
        # Low and high date
        c3.fwd(dlow1, dhigh1)
        # Low and middle date
        c3.fwd(dlow1, d)
        # Middle and high date
        c3.fwd(d, dhigh1)


if __name__ == "__main__":
    unittest.main()
