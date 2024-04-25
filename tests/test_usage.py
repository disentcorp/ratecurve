import unittest

from dateroll import Duration, ddh
from ratecurve import Curve

Duration.just_bds = lambda self, *args, **kwargs: self.just_days
Duration.yf = lambda self, *args, **kwargs: self.just_days / 365


class TestUsage(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...

    def test_fwd_with_date_and_tenor(self):
        """
        testing bug fix for curve.fwd(date,tenor) [throws error]. Tenor should computed from date in param[0].
        """
        curve_data = {"0m": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(curve_data)

        date = ddh("t+1y")
        tenor = "3m"
        # test forward call
        curve(date, tenor)

    def test_spot_at_t0(self):
        """
        testing bug fix for curve.spot(self.base). Should return earliest rate provided.
        """
        curve_data = {"4d": 0.053, "1m": 0.0548, "30y": 0.0465}
        date = ddh("t")

        # Test across different interp_ons and flat
        c1 = Curve(curve_data, interp_on="r")
        rate_1 = c1.spot(date)
        self.assertEqual(rate_1, 0.053)

        c2 = Curve(curve_data, interp_on="r*t")
        rate_2 = c2.spot(date)
        self.assertEqual(rate_2, 0.053)

        c3 = Curve(curve_data)
        rate_3 = c3.spot(date)
        self.assertEqual(rate_3, 0.053)

        # Test across different interp_ons and extrapolate
        c4 = Curve(curve_data, interp_on="r", extrap_method="extrapolate")
        rate_4 = c4.spot(date)
        self.assertLess(rate_4, 0.053)
        c5 = Curve(curve_data, interp_on="r*t", extrap_method="extrapolate")
        rate_5 = c5.spot(date)
        self.assertLess(rate_5, 0.053)
        c6 = Curve(curve_data, extrap_method="extrapolate")
        rate_6 = c6.spot(date)
        # Should be less than if interpolated properly (t+4d, .053),(t+1m, .0548)
        self.assertLess(rate_6, 0.053)

    def test_spot_before_anchor(self):
        """
        testing extrap to time before anchor dates
        """
        curve_data = {"4d": 0.053, "1m": 0.0548, "30y": 0.0465}
        date = ddh("t-1d")

        # Test across different interp_ons and flat
        c1 = Curve(curve_data, interp_on="r")
        rate_1 = c1.spot(date)
        self.assertEqual(rate_1, 0.053)

        c2 = Curve(curve_data, interp_on="r*t")
        rate_2 = c2.spot(date)
        self.assertEqual(rate_2, 0.053)

        c3 = Curve(curve_data)
        rate_3 = c3.spot(date)
        self.assertEqual(rate_3, 0.053)

        # Test across different interp_ons and extrapolate
        c4 = Curve(curve_data, interp_on="r", extrap_method="extrapolate")
        rate_4 = c4.spot(date)
        self.assertLess(rate_4, 0.053)
        c5 = Curve(curve_data, interp_on="r*t", extrap_method="extrapolate")
        rate_5 = c5.spot(date)
        self.assertLess(rate_5, 0.053)
        c6 = Curve(curve_data, extrap_method="extrapolate")
        rate_6 = c6.spot(date)
        # Should be less than if interpolated properly (t+4d, .053),(t+1m, .0548)
        self.assertLess(rate_6, 0.053)


if __name__ == "__main__":
    unittest.main()
