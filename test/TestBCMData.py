import unittest

from pybcm.bcmdata import BCMData


class TestBCMDataMethods(unittest.TestCase):

    def test_construct(self):
        bcmData = BCMData()

        self.assertEqual('foo'.upper(), 'FOO')



if __name__ == '__main__':
    unittest.main()