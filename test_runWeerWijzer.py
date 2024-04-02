from runWeerWijzer import (
    bereken_zambretti,
    bereken_voorspellingen_uren,
    post_weer_data,
    API,
    API_KEY,
)
from WeerWijzerAPI import app, get_db
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, query
from random import randint
from DB import (
    Base,
    seed_db,
    Meting,
    MetingUren,
    Voorspelling,
    VoorspellingUren,
    Locatie,
    zWaarden,
)
from multiprocessing import Process, freeze_support, active_children
import uvicorn
import requests
import time

# In-memory database opzetten voor het testen
DATABASE_URL = "sqlite:///:memory:"
TEST_API = "http://localhost:5000"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setUp():
    # Tabellen in de test database aanmaken en seed data aanmaken
    Base.metadata.create_all(bind=engine)
    seed_db(TestingSessionLocal())


def teardown():
    # Tabellen in de database verwijderen
    Base.metadata.drop_all(bind=engine)


# De database verbinding van WeerWijzerAPI overschrijven met de test database
def override_get_db():
    database = TestingSessionLocal()
    setUp()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db

locatie = "Apeldoorn"


def test_bereken_zambretti():
    assert bereken_zambretti(1000, 990, 180) == 27
    assert bereken_zambretti(945, 940, 180) == 999


def run_server():
    uvicorn.run(
        "WeerWijzerAPI:app",
        host="localhost",
        port=5000,
    )


def test_data_ophalen_en_berekenen():
    # Start the server in a separate process
    server_process = Process(target=run_server)
    server_process.start()

    # Give the server some time to start
    time.sleep(10)

    url_metinguren = TEST_API + f"/metinguren/{locatie}?api_key={API_KEY}"
    url_voorspellinguren = TEST_API + f"/voorspellinguren/{locatie}?api_key={API_KEY}"

    # Weerdata posten en voorspellinguren berekenen
    post_weer_data(locatie, TEST_API)
    print(bereken_voorspellingen_uren(locatie, TEST_API))

    # Testen
    responseGetMetingUren = requests.get(url_metinguren).json()
    responseGetVoorspellingUren = requests.get(url_voorspellinguren).json()
    assert (
        responseGetMetingUren[0]["datetime"]
        == responseGetVoorspellingUren[0]["datetime"]
    )
    for i in range(len(responseGetMetingUren)):
        if i < 2:
            continue
        assert (
            bereken_zambretti(
                responseGetMetingUren[i]["pressure"],
                responseGetMetingUren[i - 3]["pressure"],
                responseGetMetingUren[i]["winddirection"],
            )
            != 999
        )
    for i in responseGetMetingUren:
        for key, value in i.items():
            assert "None" not in str(key)
            assert "None" not in str(value)
    for i in responseGetVoorspellingUren:
        for key, value in i.items():
            assert "None" not in str(key)
            assert "None" not in str(value)

    # Stop the server
    server_process.terminate()
    server_process.join()


if __name__ == "__main__":
    test_data_ophalen_en_berekenen()
