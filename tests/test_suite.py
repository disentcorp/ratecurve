import unittest


from tests.test_curve import TestCurve


def test_suite():
    """
    add test cases into suite
    """
    suite = unittest.TestSuite(
        [
            unittest.TestLoader().loadTestsFromTestCase(TestCurve),
        ]
    )
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = test_suite()
    runner.run(suite)
