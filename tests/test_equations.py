import unittest
from dateroll import ddh, Duration
from ratecurve.utils import *
from ratecurve.equations import *
Duration.just_bds = lambda self, *args,**kwargs: self.just_days
import numpy as np

# Shorthand for e, ln
ln = np.log
e = np.e
class TestEquations(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...
    
    def test_cap_factor(self):
        r = .05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)

        self.assertEqual(cap_factor(r,t, "EXP"),e**(r*t))
        self.assertEqual(cap_factor(r, t, "LIN"),1+r*t)
        self.assertEqual(cap_factor(r, t, "YLD"),(1+r)**t)
        with self.assertRaises(Exception):
            cap_factor(r, t, "apple")


    def test_disc_factor(self):
        r = .05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)       
        self.assertEqual(disc_factor(r, t, "EXP"),1/(e**(r*t)))


    def test_convert_cap_factor_to_rate(self):
        cf = 1.05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)

        self.assertEqual(convert_cap_factor_to_rate(cf, t, "EXP"),ln(cf)/t)
        self.assertEqual(convert_cap_factor_to_rate(cf, t, "LIN"),(cf-1)/t)
        self.assertEqual(convert_cap_factor_to_rate(cf, t, "YLD"),(cf**(1/t)) - 1)
        with self.assertRaises(Exception):
            convert_cap_factor_to_rate(cf, t, "apple")
    
    def test_convert_disc_factor_to_rate(self):
        df = .97
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)
        self.assertEqual(convert_disc_factor_to_rate(df, t, "EXP"),(ln(1/df)/t))

if __name__ == "__main__":
    unittest.main()
