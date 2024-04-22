import datetime
import unittest

from dateroll import Duration, ddh
from ratecurve import utils

Duration.just_bds = lambda self, *args, **kwargs: self.just_days
Duration.yf = lambda self, *args, **kwargs: self.just_days / 365


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls): ...

    @classmethod
    def tearDownClass(self): ...

    def test_isdatelike(self):
        """
        testing date detector
        """
        good_date = ddh("t")
        good_string = "1/1/2000"
        bad_string = "apple"
        bad_type = 5
        self.assertEqual(utils.isdatelike(good_date), True)
        self.assertEqual(utils.isdatelike(good_string), True)
        self.assertEqual(utils.isdatelike(bad_string), False)
        self.assertEqual(utils.isdatelike(bad_type), False)

    def test_to_dateroll_date(self):
        """
        testing conversion to dateroll.date
        """
        good_date = ddh("t")
        bad_date = datetime.date.today()
        good_string_tenor = "3m"
        bad_string = "apple"
        bad_type = 5
        # with base
        good_base = ddh("1/1/2000")
        bad_base = "apple"
        self.assertEqual(
            utils.to_dateroll_date(good_string_tenor, good_base),
            good_base + ddh(good_string_tenor),
        )
        with self.assertRaises(Exception):
            utils.to_dateroll_date(bad_date, good_base)
            utils.to_dateroll_date(good_string_tenor, bad_base)
        # without base
        self.assertEqual(utils.to_dateroll_date(good_date), ddh("t"))
        with self.assertRaises(Exception):
            utils.to_dateroll_date(good_string_tenor)
            utils.to_dateroll_date(bad_string)
            utils.to_dateroll_date(bad_type)

    def test_from_date_to_number(self):
        """
        testing date to number conversion utility given root date and calendar
        """
        cal = "ALL"
        root = ddh("1/1/2000")
        good_date = ddh("t")
        bad_type = 5
        self.assertEqual(
            utils.from_date_to_number(good_date, root, "ACT/365", cal),
            (good_date - root).just_days,
        )
        self.assertEqual(
            utils.from_date_to_number(good_date, root, "bd/252", cal),
            (good_date - root).just_days,
        )
        with self.assertRaises(Exception):
            utils.from_date_to_number(bad_type, root, "ACT/365", cal)

    def test_from_number_to_date(self):
        """
        testing inverse of date to number
        """
        cal = "ALL"
        root = ddh("1/1/2000")
        number = 10
        dc = "ACT/365"
        self.assertEqual(
            utils.from_number_to_date(number, root, dc, cal), root + number
        )

    def test_delta_t(self):
        """
        testing year fraction calculator delta_t
        """
        date1 = ddh("t")
        date2 = ddh("t+5")
        dc = "ACT/365"
        cal = "ALL"
        self.assertEqual(
            utils.delta_t(date1, date2, dc, cal), (date2 - date1).yf(cal, dc)
        )


if __name__ == "__main__":
    unittest.main()
