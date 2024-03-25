import json
from fastapi.testclient import TestClient
from WeerWijzerAPI import (
    app,
    metinguren_uit_database_halen,
    create_meting,
    get_metingen,
    get_locaties,
)
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

testing_config = {
    "user": os.environ.get("TEST_DB_USER"),
    "password": os.environ.get("TEST_DB_PASSWORD"),
    "host": os.environ.get("TEST_DB_HOST"),
    "port": os.environ.get("TEST_DB_PORT"),
    "database": os.environ.get("TEST_DB_NAME"),
}


def test_metinguren_uit_database_halen():
    assert metinguren_uit_database_halen() is not None


def test_get_metingen():
    for index, i in enumerate(get_metingen()):
        for j in i:
            key, value = j
            if key == "datetime":
                try:
                    test_date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return AssertionError(index, "Invalid datetime format:", value)
                if index == 0:
                    assert test_date <= datetime.now()
            if key == "pressure":
                assert value >= 947
                assert value <= 1050


def test_get_locaties():
    for index, i in enumerate(get_locaties()):
        assert i["locatieId"] == index + 1
        assert i["locatie"] is not None


# POSTS MOETEN NOG GEBEUREN
