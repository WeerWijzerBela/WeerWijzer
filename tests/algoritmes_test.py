import pytest
import os
import sys

# Het pad naar het bestand in de home directory van de gebruiker
file_path = os.path.expanduser("~/runWeerWijzer.py")

# Controleer of het bestand bestaat
if os.path.isfile(file_path):
    # Voeg het pad toe aan het systeem pad, zodat Python het kan vinden
    sys.path.append(os.path.dirname(file_path))

    # Importeer de inhoud van het bestand
    from runWeerWijzer import *
else:
    print("Bestand niet gevonden:", file_path)


class TestWeerberekenen:
    def test_zambretti(self):
        assert bereken_zambretti(1000, 990, 180) == 27

    def test_zambretti_onvoorspelbaar(self):
        assert bereken_zambretti(945, 940, 180) == 5



if __name__ == "__main__":
    pytest.main()
