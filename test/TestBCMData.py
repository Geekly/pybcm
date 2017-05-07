import unittest
import pybcm


class TestBCMDataMethods(unittest.TestCase):

    def test_construct(self):
        bcmData = pybcm.BCMData()

        self.assertEqual('foo'.upper(), 'FOO')



if __name__ == '__main__':
    unittest.main()