# Import runWeerWijzer 1 directory hoger
import pytest
from pathlib import Path
import sys
parent_path = Path(__file__).resolve().parents[1]
sys.path.append(str(parent_path))
from runWeerWijzer import *




class TestWeerberekenen:
    def test_zambretti(self):
        assert bereken_zambretti(1000, 990, 180) == 27

    def test_zambretti_onvoorspelbaar(self):
        assert bereken_zambretti(945, 940, 180) == 999



if __name__ == "__main__":
    pytest.main()
