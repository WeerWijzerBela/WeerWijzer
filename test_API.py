from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from DB import Base, init_db, seed_db, zWaarden
from WeerWijzerAPI import app, get_db, verify_api_key
from runWeerWijzer import bereken_voorspellingen_uren, bereken_zambretti
from datetime import datetime, timedelta
import os
import pytest

# TestClient opzetten
client = TestClient(app)

# In-memory database opzetten voor het testen
DATABASE_URL = "sqlite:///:memory:"
API_KEY = os.environ.get("API_KEY")
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# De database verbinding van WeerWijzerAPI overschrijven met de test database
def override_get_db():
    database = TestingSessionLocal()
    setUp()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


# Waardes voor testen
datumNuTesting = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
locatie = "Testing"


def test_verify_api_key():
    # Test bad API key
    with pytest.raises(Exception) as e_info:
        verify_api_key()

    # Test good API key
    assert verify_api_key(API_KEY) is True


def test_empty_get_locatie(standalone=True):
    setUp()
    response = client.get("/locaties/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []
    if standalone:
        teardown()


def test_empty_delete_locatie(standalone=True):
    setUp()
    response = client.delete(f"/locaties/Amersfoort?api_key={API_KEY}")
    assert response.status_code == 404, response.text
    if standalone:
        teardown()


def test_create_locatie(standalone=True):
    setUp()
    locatie = "Testing"
    locatieId = 999
    # Kijken of de locatie niet bestaat
    response = client.delete(f"/locaties/{locatie}?api_key={API_KEY}")
    assert response.status_code == 404, response.text

    response = client.post(
        f"/locaties?api_key={API_KEY}",
        json={"locatieId": locatieId, "locatie": locatie},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["locatie"] == locatie
    assert "locatieId" in data
    if standalone:
        teardown()


def test_delete_locatie(standalone=True):
    test_create_locatie()
    nieuweLocatie = "NieuweTest"
    # Aanmaken van een tweede locatie zodat de database niet leegraakt
    response = client.post(
        f"/locaties?api_key={API_KEY}",
        json={"locatieId": 998, "locatie": nieuweLocatie},
    )
    assert response.status_code == 200, response.text
    # Toevoegen van metingen, metinguren, voorspellingen en voorspellinguren aan locatie
    test_create_voorspellinguren(False)
    # Verwijderen van de eerste locatie
    response = client.delete(f"/locaties/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text
    if standalone:
        teardown()


def test_create_meting(standalone=True):
    test_create_locatie(False)
    response = client.post(
        f"/metingen?api_key={API_KEY}",
        json={"locatie": locatie, "datetime": datumNuTesting},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["locatie"] == locatie
    assert data["datetime"] == datumNuTesting
    if standalone:
        teardown()


def test_create_metinguren(standalone=True):
    test_create_meting(False)
    global tijdMin2hrs
    tijdNu = datetime.now()
    tijdMin1hrs = tijdNu - timedelta(hours=1)
    tijdMin2hrs = tijdNu - timedelta(hours=2)
    response = client.post(
        f"/metinguren?api_key={API_KEY}",
        json=[
            {
                "datetime": tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "temperature": 19,
                "pressure": 993,
                "winddirection": 170,
            },
            {
                "datetime": tijdMin1hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "temperature": 18,
                "pressure": 994,
                "winddirection": 180,
            },
            {
                "datetime": tijdNu.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "temperature": 17,
                "pressure": 998,
                "winddirection": 190,
            },
        ],
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["datetime"] == tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    assert data[0]["temperature"] == 19
    assert data[0]["pressure"] == 993
    assert data[0]["winddirection"] == 170
    if standalone:
        teardown()


# READ_METING KAN GEEN GET METINGUREN ZIJN. RESPONSE MOET AANGEPAST WORDEN, ER MOETEN TWEE CREATES GEMAAKT WORDEN OM EEN TE KUNNEN TESTEN
def test_read_metingen_via_metinguren(standalone=True):
    test_create_metinguren(False)
    response = client.get(f"/metinguren/{locatie}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["datetime"] == tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%f")
    assert data[0]["temperature"] == 19
    assert data[0]["pressure"] == 993
    assert data[0]["winddirection"] == 170
    if standalone:
        teardown()


# DE RETURN VAN DELETE METINGEN MOET AANGEPAST WORDEN. EN DE COUNT ERVAN MOET GETELD WORDEN, OM TE KIJKEN OF DIT MATCHT
def test_delete_metingen(standalone=True):
    test_create_metinguren(False)
    response = client.delete(f"/metingen/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text
    assert "Deze wordt niet verwijderd." in response.text
    # Test of hij als eerst succesvol checkt of er maar een meting is die minder dan 12 uur oud is.

    # Aanmaken van een tweede meting die wel ouder is dan 12 uur om te kijken of deze wel verwijderd is
    datum24uurGeleden = datetime.now() - timedelta(hours=24)

    response = client.post(
        f"/metingen?api_key={API_KEY}",
        json={
            "locatie": locatie,
            "datetime": datum24uurGeleden.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    )

    assert response.status_code == 200, response.text

    response = client.post(
        f"/metinguren?api_key={API_KEY}",
        json=[
            {
                "datetime": tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "temperature": 19,
                "pressure": 993,
                "winddirection": 170,
            }
        ],
    )
    assert response.status_code == 200, response.text

    response = client.delete(f"/metingen/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text
    assert "zijn verwijderd." in response.text

    if standalone:
        teardown()


def test_create_voorspelling(standalone=True):
    test_create_metinguren(False)
    response = client.post(
        f"/voorspellingen?api_key={API_KEY}",
        json={
            "locatie": locatie,
            "datetime": tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    )
    assert response.status_code == 200, response.text
    if standalone:
        teardown()


def test_create_voorspellinguren(standalone=True):
    test_create_voorspelling(False)
    response = client.get(f"/metinguren/{locatie}")
    jsonData = response.json()

    zambrettiList = []
    for i in range(0, len(jsonData), 1):
        if 0 < i < 5:
            continue
        huidige_meting = jsonData[i]
        vorige_meting = jsonData[1] if i == 0 else jsonData[i - 3]
        zambretti_value = bereken_zambretti(
            huidige_meting["pressure"],
            vorige_meting["pressure"],
            windrichting=huidige_meting["winddirection"],
        )
        zambrettiList.append(
            {
                "datetime": huidige_meting["datetime"],
                "temperature": huidige_meting["temperature"],
                "zWaarde": zambretti_value,
            }
        )

    response = client.post(f"/voorspellinguren?api_key={API_KEY}", json=zambrettiList)
    assert response.status_code == 200, response.text

    if standalone:
        teardown()


def test_get_voorspellinguren(standalone=True):
    test_create_voorspellinguren(False)
    response = client.get(f"/voorspellinguren/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["datetime"] == tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%f")

    if standalone:
        teardown()


def test_delete_voorspelling(standalone=True):
    test_create_voorspellinguren(False)
    # Tweede voorspelling aanmaken
    response = client.post(
        f"/voorspellingen?api_key={API_KEY}",
        json={
            "locatie": locatie,
            "datetime": tijdMin2hrs.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"voorspellinguren?api_key={API_KEY}",
        json=[
            {
                "datetime": "2024-04-02T16:00:00.000000",
                "temperature": 19.0,
                "zWaarde": 16,
                "beschrijving": "Unsettled, Rain at Times",
                "sneeuw": False,
            }
        ],
    )
    assert response.status_code == 200, response.text

    response = client.delete(f"/voorspellingen/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text

    if standalone:
        teardown()


def setUp():
    # Tabellen in de test database aanmaken
    Base.metadata.create_all(bind=engine)
    zWaardenToevoegen()


def teardown():
    # Tabellen in de database verwijderen
    Base.metadata.drop_all(bind=engine)


def zWaardenToevoegen():
    db = TestingSessionLocal()
    if db.query(zWaarden).count() == 0:
        zWaardenData = [
            zWaarden(zWaarde=i, beschrijving=beschrijving)
            for i, beschrijving in enumerate(
                [
                    "Mooi weer komt eraan.",
                    "Het weer blijft mooi.",
                    "Het mooie weer verandert naar slechter.",
                    "Redelijk mooi weer, maar het wordt slechter.",
                    "Kans op neerslag, het wordt onrustiger.",
                    "Het wordt onrustig, later neerslag.",
                    "Af en toe neerslag, het wordt slechter.",
                    "Meer neerslag, wordt zeer slecht.",
                    "Zeer onrustig weer, met neerslag.",
                    "Rustig en mooi weer op komst.",
                    "Mooi weer in aantocht.",
                    "Mooi weer op komst, maar mogelijk buien.",
                    "Redelijk mooi weer, waarschijnlijk buien.",
                    "Buien met af en toe opklaringen.",
                    "Veranderlijk weer, met enkele regenbuien.",
                    "Onrustig weer, af en toe regen.",
                    "Regen met regelmatige tussenpozen.",
                    "Zeer onrustig weer, regen verwacht.",
                    "Stormachtig weer, met veel regen.",
                    "Rustig en mooi weer op komst.",
                    "Mooi weer in aantocht.",
                    "Het wordt mooi weer.",
                    "Het weer wordt redelijk mooi, verbeterend.",
                    "Redelijk mooi weer, mogelijk buien.",
                    "Vroege buien, maar verbeterend.",
                    "Veranderlijk weer, maar het wordt beter.",
                    "Tamelijk onrustig weer, later opklarend.",
                    "Het wordt onrustig, maar waarschijnlijk verbeterend.",
                    "Onrustig weer, met korte mooie periodes.",
                    "Zeer onrustig weer, kan leiden tot storm.",
                    "Stormachtig weer, mogelijk verbeterend.",
                    "Stormachtig weer, met veel regen.",
                ],
                start=1,
            )
        ]
        db.add_all(zWaardenData)
        db.commit()
