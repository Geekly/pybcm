import unittest

from pybcm.blrest_wrapper import rest_wrapper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.pc = rest_wrapper('../config/bcm.ini')
        pass

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
