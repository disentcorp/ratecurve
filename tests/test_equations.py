import unittest

import numpy as np
from dateroll import Duration, ddh
from ratecurve import equations, utils

Duration.just_bds = lambda self, *args, **kwargs: self.just_days
# Shorthand for e, ln
ln = np.log
e = np.e


class TestEquations(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...

    def test_cap_factor(self):
        """
        test cap factor equation across different methods
        """
        r = 0.05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh("t")
        d2 = ddh("t+1y")
        t = utils.delta_t(d1, d2, dc, cal)

        self.assertEqual(equations.cap_factor(r, t, "EXP"), e ** (r * t))
        self.assertEqual(equations.cap_factor(r, t, "LIN"), 1 + r * t)
        self.assertEqual(equations.cap_factor(r, t, "YLD"), (1 + r) ** t)
        with self.assertRaises(Exception):
            equations.cap_factor(r, t, "apple")

    def test_disc_factor(self):
        """
        test disc factor equation across different methods
        """
        r = 0.05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh("t")
        d2 = ddh("t+1y")
        t = utils.delta_t(d1, d2, dc, cal)
        self.assertEqual(equations.disc_factor(r, t, "EXP"), 1 / (e ** (r * t)))

    def test_convert_cap_factor_to_rate(self):
        """
        test conversion of cap factor to rate across different methods
        """
        cf = 1.05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh("t")
        d2 = ddh("t+1y")
        t = utils.delta_t(d1, d2, dc, cal)

        self.assertEqual(equations.convert_cap_factor_to_rate(cf, t, "EXP"), ln(cf) / t)
        self.assertEqual(
            equations.convert_cap_factor_to_rate(cf, t, "LIN"), (cf - 1) / t
        )
        self.assertEqual(
            equations.convert_cap_factor_to_rate(cf, t, "YLD"), (cf ** (1 / t)) - 1
        )
        with self.assertRaises(Exception):
            equations.convert_cap_factor_to_rate(cf, t, "apple")

    def test_convert_disc_factor_to_rate(self):
        """
        test conversion of disc factor to rate (methods already tested in cap factor)
        """
        df = 0.97
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh("t")
        d2 = ddh("t+1y")
        t = utils.delta_t(d1, d2, dc, cal)
        self.assertEqual(
            equations.convert_disc_factor_to_rate(df, t, "EXP"), (ln(1 / df) / t)
        )


if __name__ == "__main__":
    unittest.main()
