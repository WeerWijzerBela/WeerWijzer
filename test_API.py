from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from DB import Base, init_db
from WeerWijzerAPI import app, get_db
from datetime import datetime, timedelta
import os
from datetime import datetime

# TestClient opzetten
client = TestClient(app)

# In-memory database opzetten voor het testen
DATABASE_URL = "sqlite:///test.db"
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

datumNuTesting = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def test_empty_get_locaties(standalone=True):
    setUp()
    response = client.get("/locaties/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []
    if standalone:
        teardown()

def test_empty_delete_locaties(standalone=True):
    setUp() 
    response = client.delete(f"/locaties/Amersfoort?api_key={API_KEY}")
    assert response.status_code == 404, response.text
    if standalone:
        teardown()

def test_create_locaties(standalone=True):
    setUp()
    response = client.post(f"/locaties?api_key={API_KEY}", json={"locatieId": "1", "locatie": "Apeldoorn"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["locatie"] == "Apeldoorn"
    assert "locatieId" in data
    if standalone:
        teardown()

def test_create_meting(standalone=True):
    test_create_locaties(False)
    response = client.post(
        f"/metingen?api_key={API_KEY}", json={"locatie": "Apeldoorn", "datetime": datumNuTesting}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["locatie"] == "Apeldoorn"
    assert data["datetime"] == datumNuTesting
    if standalone:
        teardown()


# READ_METING KAN GEEN GET METINGUREN ZIJN. RESPONSE MOET AANGEPAST WORDEN, ER MOETEN TWEE CREATES GEMAAKT WORDEN OM EEN TE KUNNEN TESTEN
def test_read_metingen_via_metinguren(standalone=True):
    test_create_meting(False)
    locatie = "Apeldoorn"
    response = client.post(
        f"/metingen?api_key={API_KEY}", json={"locatie": locatie, "datetime": datumNuTesting}
    )
    assert response.status_code == 200, response.text
    data = response.json()

    response = client.get(f"/metinguren/{locatie}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["locatie"] == locatie
    assert data["datetime"] == datumNuTesting
    print(data["datetime"])
    print(datumNuTesting)
    if standalone:
        teardown()


# DE RETURN VAN DELETE METINGEN MOET AANGEPAST WORDEN. EN DE COUNT ERVAN MOET GETELD WORDEN, OM TE KIJKEN OF DIT MATCHT
def test_delete_metingen(standalone=True):
    test_create_meting(False)
    item_id = 1
    locatie = "Apeldoorn"
    response = client.delete(f"/metingen/{locatie}?api_key={API_KEY}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == item_id
    # Try to get the deleted item
    response = client.get(f"/metingen/{locatie}")
    assert response.status_code == 404, response.text
    if standalone:
        teardown()

def test_connection_with_ext_API(standalone=True):
    setUp()
    ### CODE HIER ###
    if standalone:
        teardown()
    


def setUp():
    # Tabellen in de test database aanmaken
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Tabellen in de database verwijderen
    Base.metadata.drop_all(bind=engine)
