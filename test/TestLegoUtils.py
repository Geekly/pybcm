import unittest
from pybcm.legoutils import *


class TestLegoUtils(unittest.TestCase):

    def testIsValidColor(self):

        self.assertTrue(58 in LEGOCOLORS)
        self.assertFalse(230 in LEGOCOLORS)

    def testJoinElement(self):
        A = "3456"
        B = "34"
        C = LegoElement.joinElement(A, B)

        self.assertEquals(C, "3456|34")

    def testSplitElement(self):
        A, B = LegoElement.splitElement("3456|34")

        self.assertEquals(A, "3456")
        self.assertEquals(B, "34")

    def testProperties(self):
        element = LegoElement('3450', '2', 299)
        self.assertEquals('3450|2', element.elementId)
        self.assertEquals('3450|2', str(element))
        self.assertEquals(299, element.wantedqty)


