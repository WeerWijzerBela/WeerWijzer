import unittest
from metingen import *
from weerberekenen import *
from DB import *

class TestMetingen(unittest.TestCase):
    def setUp(self):
        #Testdata inladen
        self.app = App(database="test_metingen.json")
    def test_function1(self):
        # Test cases for function 1 in metingen.py
        # Add your test cases here
        pass

    def test_function2(self):
        # Test cases for function 2 in metingen.py
        # Add your test cases here
        pass

    # Add more test functions for other functions in metingen.py

class TestWeerberekenen(unittest.TestCase):
    def test_function1(self):
        # Test cases for function 1 in weerberekenen.py
        # Add your test cases here
        pass

    def test_function2(self):
        # Test cases for function 2 in weerberekenen.py
        # Add your test cases here
        pass

    # Add more test functions for other functions in weerberekenen.py

class TestWeerberekenen(unittest.TestCase):
    def test_zambretti(self):
        #Controleren of de Zambretti functie juist wordt berekend
        self.assertEqual(Zambretti(1000, 990, 180), 27)
        pass
    def test_zambretti_onvoorspelbaar(self):
        #Controleren of de Zambretti functie juist wordt geretourneerd, bij een onvoorspelbare situatie
        self.assertEqual(Zambretti(945, 940, 180), 999)
        pass

class TestDB(unittest.TestCase):
    def test_database_connectie(self):
        try:
            self.assertIsNotNone(DB.connect_to_database(), "Database connectie is niet gelukt")
        except Exception:
            return Exception

    def test_function2(self):
        try:
            post_external_data()
        except Exception: 
            return Exception
        # Test cases for function 2 in DB.py
        # Add your test cases here
        pass

    # Add more test functions for other functions in DB.py

if __name__ == '__main__':
    unittest.main()