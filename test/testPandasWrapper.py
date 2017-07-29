import unittest

from pybcm.pandas_wrapper import PandasClient


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.pc = PandasClient('../config/bcm.ini')
        pass

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
