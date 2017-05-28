import unittest
from pybcm.legoutils import *
import logging


class TestLegoUtils(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger("TestLegoUtils")

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

    def testLegoColor(self):
        color1 = LegoColor(71)
        color2 = LegoColor('71')

        # 71: 'Magenta'
        self.assertEquals(color1.name, 'Magenta')
        self.assertEquals(color1.name, color2.name)
        with self.assertRaises(KeyError) as context:
            print(context)
            color3 = LegoColor(450)

        print(color1)

    def testLegoElement(self):
        element1 = LegoElement(4321, 86)
        print(element1)
        print(element1.color)
        print(element1.colorName)

