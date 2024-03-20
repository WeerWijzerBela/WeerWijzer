import pytest

# # Import runWeerWijzer 1 directory hoger
# from pathlib import Path
# import sys
# parent_path = Path(__file__).resolve().parents[1]
# sys.path.append(str(parent_path))
from runWeerWijzer import bereken_zambretti


class TestWeerberekenen:
    def test_zambretti(self):
        assert bereken_zambretti(1000, 990, 180) == 27

    def test_zambretti_onvoorspelbaar(self):
        assert bereken_zambretti(945, 940, 180) == 5



if __name__ == "__main__":
    pytest.main()
