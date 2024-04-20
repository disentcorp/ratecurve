import unittest
import datetime
from dateroll import ddh, Duration
from ratecurve.utils import *
from ratecurve.equations import *
Duration.just_bds = lambda self, *args,**kwargs: self.just_days

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

        cap_factor(r,t, "EXP")
        cap_factor(r, t, "LIN")
        cap_factor(r, t, "YLD")
        with self.assertRaises(Exception):
            cap_factor(r, t, "apple")


    def test_disc_factor(self):
        r = .05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)       
        disc_factor(r, t, "EXP")


    def test_convert_cap_factor_to_rate(self):
        cf = 1.05
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)

        convert_cap_factor_to_rate(cf, t, "EXP")
        convert_cap_factor_to_rate(cf, t, "LIN")
        convert_cap_factor_to_rate(cf, t, "YLD")
        with self.assertRaises(Exception):
            convert_cap_factor_to_rate(cf, t, "apple")
    
    def test_convert_disc_factor_to_rate(self):
        df = .97
        dc = "ACT/365"
        cal = "ALL"
        d1 = ddh('t')
        d2 = ddh('t+1y')
        t = delta_t(d1, d2, dc, cal)
        convert_disc_factor_to_rate(df, t, "EXP")

if __name__ == "__main__":
    unittest.main()
