from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import DB
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles



app = FastAPI()
# command to start: uvicorn WeerWijzerAPI:app --reload
class WeerMeting(BaseModel):
    '''Klasse voor het aanmaken van een NieuweWeerMeting object.'''
    locatie: str
    datetime: str


class WeerMetingUren(BaseModel):
    '''Klasse voor het aanmaken van een WeerMeting object.'''
    datetime: str
    temperature: float
    pressure: float
    winddirection: float


class Locatie(BaseModel):
    '''Klasse voor het aanmaken van een Locatie object.'''
    locatieId: int
    locatie: str


class Voorspelling(BaseModel):
    '''Klasse voor het aanmaken van een Verwachting object.'''
    locatie: str
    datetime: str


class VoorspellingUren(BaseModel):
    '''Klasse voor het aanmaken van een VerwachtingUren object.'''
    datetime: str
    temperature: float
    zWaarde: int

def uren_uit_database_halens(location):
    '''Haal metingen uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            f"SELECT * FROM {location}uren WHERE {location}enId = (SELECT MAX(m2.{location}enId) FROM {location}uren m2) ORDER BY {location}UrenId ASC;")
        metingen = cursor.fetchall()
        return metingen
    except Exception:
        connection.close()
    finally:
        connection.close()

# @app.get('/')
# def get_locaties():
#     return "Halowa"
@app.get('/')
def index() -> HTMLResponse:
    # Hier kan je extra logica toevoegen voordat de webserver start, indien nodig
    #run(host='localhost', port=8000)
    #file = codecs.open("index.html", 'r', "utf-8")
    with open("templates/index.html", "r") as file:
        html_content = file.read()
    return html_content
    # Hier geef je een HTML-bestand terug of voer je andere acties uit

# ALLE ENDPOINTS
########################################################################################################################
# METINGEN / METINGUREN ENDPOINTS
@app.get('/metinguren')
def get_metingen() -> List[WeerMetingUren]:
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    metingen = uren_uit_database_halens('meting')
    weermetingen = []
    for meting in metingen:
        meting['datetime'] = str(meting['datetime'])
        weermetingen.append(WeerMetingUren(**meting))
    return weermetingen


@app.post('/metingen')
def create_meting(nieuwe_meting: WeerMeting) -> List[WeerMeting]:
    '''Voeg een nieuwe meting toe aan de database en retourneer een NieuweWeerMeting object.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO metingen (locatieId, datetime) "
            f"VALUES ((SELECT locatieId FROM locaties WHERE locatie = %s), %s)",
            (nieuwe_meting.locatie, nieuwe_meting.datetime)
        )
        connection.commit()
        return {
            **nieuwe_meting.dict()
        }
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.post('/metinguren')
def create_meting_uren_batch(nieuwe_metingen: List[WeerMetingUren]) -> List[WeerMetingUren]:
    '''Voeg nieuwe metingen toe aan de database en retourneer een lijst met NieuweWeerMetingUren objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        metingen_values = []
        for meting in nieuwe_metingen:
            metingen_values.append((
                meting.datetime, meting.temperature, meting.pressure, meting.winddirection
            ))
        cursor.executemany(
            "INSERT INTO metinguren (metingenId, datetime, temperature, pressure, winddirection) "
            f"VALUES ((SELECT metingenId FROM metingen ORDER BY metingenId DESC LIMIT 1), %s, %s, %s, %s)",
            metingen_values
        )
        connection.commit()
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/metingen")
def delete_metingen():
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM metingen")
        count = cursor.fetchone()[0]
        if count <= 1:
            raise HTTPException(status_code=400,
                                detail="Metingen verwijderen is niet mogelijk: Er is maar één meting opgeslagen.")
        cursor.execute("SELECT metingenId FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR")
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM metinguren WHERE metingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR")
        connection.commit()
        return {"detail": f"{len(old_measurement_ids)} metingen zijn verwijderd."}
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=202)


########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get('/voorspellinguren')
def get_voorspellingen() -> List[VoorspellingUren]:
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van voorspellinguren objecten.'''
    voorspellingen = uren_uit_database_halens('voorspelling')
    weervoorspelling = []
    for voorspelling in voorspellingen:
        voorspelling['datetime'] = str(voorspelling['datetime'])
        weervoorspelling.append(VoorspellingUren(**voorspelling))
    return weervoorspelling

@app.post('/voorspellingen')
def create_voorspelling(nieuwe_voorspelling: Voorspelling) -> Voorspelling:
    '''Voeg een nieuwe voorspelling toe aan de database en retourneer een NieuweVoorspelling object.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO voorspellingen (locatieId, datetime) "
            f"VALUES ((SELECT locatieId FROM locaties WHERE locatie = %s), %s)",
            (nieuwe_voorspelling.locatie, nieuwe_voorspelling.datetime)
        )
        connection.commit()
        return {
            **nieuwe_voorspelling.dict()
        }
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.post('/voorspellinguren')
def create_voorspelling_uren_batch(nieuwe_voorspellingen: List[VoorspellingUren]) -> List[VoorspellingUren]:
    '''Voeg nieuwe voorspellingen toe aan de database en retourneer een lijst met NieuweVoorspellingUren objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        voorspellingen_values = []
        for voorspelling in nieuwe_voorspellingen:
            voorspellingen_values.append((
                voorspelling.datetime, voorspelling.temperature, voorspelling.zWaarde
            ))
        cursor.executemany(
            "INSERT INTO voorspellinguren (voorspellingenId, datetime, temperature, zWaarde) "
            f"VALUES ((SELECT voorspellingenId FROM voorspellingen ORDER BY voorspellingenId DESC LIMIT 1), %s, %s, %s)",
            voorspellingen_values
        )
        connection.commit()
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/voorspellingen")
def delete_voorspellingen():
    '''Verwijderen van voorspellingen en voorspellinguren behalve de meest recente.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT voorspellingenId FROM voorspellingen ORDER BY datetime DESC LIMIT 1")
        latest_prediction_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM voorspellinguren WHERE voorspellingenId != %s", (latest_prediction_id,))
        cursor.execute("DELETE FROM voorspellingen WHERE voorspellingenId != %s", (latest_prediction_id,))
        connection.commit()
    except Exception:
        connection.close()
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=202)

