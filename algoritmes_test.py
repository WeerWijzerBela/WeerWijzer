import unittest
from metingen import *
from runWeerWijzer import *


class TestWeerberekenen(unittest.TestCase):
    def test_zambretti(self):
        self.assertEqual(bereken_zambretti(1000, 990, 180), 27)

    def test_zambretti_onvoorspelbaar(self):
        self.assertEqual(bereken_zambretti(945, 940, 180), 999)


if __name__ == "__main__":
    unittest.main()