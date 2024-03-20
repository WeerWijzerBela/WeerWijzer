import pytest


from runWeerWijzer import *



class TestWeerberekenen:
    def test_zambretti(self):
        assert bereken_zambretti(1000, 990, 180) == 27

    def test_zambretti_onvoorspelbaar(self):
        assert bereken_zambretti(945, 940, 180) == 5



if __name__ == "__main__":
    pytest.main()
