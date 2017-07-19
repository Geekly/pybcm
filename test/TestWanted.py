import unittest

from pybcm.wanted import *


class TestWanted(unittest.TestCase):

    _wantedDict = WantedDict()

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        log = logging.getLogger("TestWanted.setUpClass")
        log.debug('test debug')
        print("Setting up wanted.py tests")
        # print(os.getcwd())

        cls._wantedlistfilename = "Sampledata/Remaining Falcon.bsx"
        cls._wantedDict.read(cls._wantedlistfilename)
        print("why isn't this printing?")
        print(cls._wantedDict)

    def testProperties(self):
        log = logging.getLogger("TestWanted.testProperties")
        self.assertEquals(__class__._wantedDict.unique_items, 5)
        self.assertEquals(__class__._wantedDict.total_items, 36)

        log.info("class loading:" + str(__class__._wantedlistfilename))

    def testFirst(self):
        log = logging.getLogger("TestWanted.testFirst")
        log.info("\nWanted List:\n" + str(__class__._wantedDict))
        self.assertTrue(True)

    def testGetQty(self):
        print(__class__)