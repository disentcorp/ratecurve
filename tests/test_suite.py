import unittest

from tests.test_curve import TestCurve
from tests.test_equations import TestEquations
from tests.test_usage import TestUsage
from tests.test_utils import TestUtils


def test_suite():
    """
    add test cases into suite
    """
    suite = unittest.TestSuite(
        [
            unittest.TestLoader().loadTestsFromTestCase(TestCurve),
            unittest.TestLoader().loadTestsFromTestCase(TestEquations),
            unittest.TestLoader().loadTestsFromTestCase(TestUtils),
            unittest.TestLoader().loadTestsFromTestCase(TestUsage),
        ]
    )
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = test_suite()
    runner.run(suite)
