import datetime
import unittest

from dateroll import Duration, ddh
from ratecurve import Curve
from ratecurve import equations
from ratecurve import utils

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
        curve_data = {"0m": 0.053, "1m": 0.0548, "30y": 0.0465}
        curve = Curve(curve_data)

        date = ddh("t")
        # test spot call
        rate_0 = curve.spot(date)
        self.assertEqual(rate_0, .053)





if __name__ == "__main__":
    unittest.main()
