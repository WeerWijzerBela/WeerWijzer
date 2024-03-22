from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from logfiles.log import logging
import DB
import os

API_KEY = os.environ.get("API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    beschrijving: Optional[str] = None
    sneeuw: Optional[bool] = None

class Image(BaseModel):
    '''Klasse voor het aanmaken van een Locatie object.'''
    imageId: int
    image: str

def verify_api_key(api_key: str = None):
    if api_key is None or api_key != API_KEY:
        logging.warning("[API] 403: Request met een ongeldige API-sleutel.")
        raise HTTPException(status_code=403, detail="Ongeldige API-sleutel")
    return True

@app.get('/')
def index():
    # Print de html pagina
    return FileResponse("templates/weerwijzer.html")

# ALLE ENDPOINTS
########################################################################################################################
# METINGEN / METINGUREN ENDPOINTS
@app.get('/metinguren/{locatie}')
def get_metingen(locatie: str) -> List[WeerMetingUren]:
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT mu.* FROM metinguren AS mu JOIN metingen AS m ON mu.metingenId = m.metingenId JOIN ( SELECT MAX(metingenId) AS max_metingenId FROM metingen AS m JOIN locaties AS l ON m.locatieId = l.locatieId WHERE l.locatie = %s) AS max_metingen ON m.metingenId = max_metingen.max_metingenId ORDER BY mu.metingUrenId ASC;",
            (locatie,))
        metingen = cursor.fetchall()
        weermetingen = []
        for meting in metingen:
            meting['datetime'] = str(meting['datetime'])
            weermetingen.append(WeerMetingUren(**meting))
        return weermetingen
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij get-request metinguren/{locatie}", e)
    finally:
        connection.close()

@app.post('/metingen')
def create_meting(nieuwe_meting: WeerMeting, key: str = Depends(verify_api_key)) -> List[WeerMeting]:
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
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het toevoegen van een nieuwe meting, {nieuwe_meting.locatie}, {nieuwe_meting.datetime}", e)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.post('/metinguren')
def create_meting_uren_batch(nieuwe_metingen: List[WeerMetingUren], key: str = Depends(verify_api_key)) -> List[WeerMetingUren]:
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
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het toevoegen van nieuwe metinguren.", e)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/metingen/{locatie}")
def delete_metingen(locatie: str, key: str = Depends(verify_api_key)):
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()
        locatieId = locatieId[0]
        cursor.execute("SELECT COUNT(*) FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
                       (locatieId,))
        count = cursor.fetchone()[0]
        if count == 0:
            logging.warning(f"[API] 200 ACCEPTED: 404: Er zijn geen metingen ouder dan 12 uur voor {locatie}.")
            return {"detail": f"Er zijn geen metingen ouder dan 12 uur voor {locatie}."}

        cursor.execute("SELECT metingenId FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
                       (locatieId,))
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM metinguren WHERE metingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
                       (locatieId,))
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het delete-request van /metingen/{locatie}.", e)
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()


########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get('/voorspellinguren/{locatie}')
def get_voorspellingen(locatie: str) -> List[VoorspellingUren]:
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van voorspellinguren objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT vu.*, z.beschrijving, CASE WHEN vu.temperature <= -5 THEN TRUE ELSE FALSE END AS sneeuw FROM voorspellinguren AS vu JOIN voorspellingen AS v ON vu.voorspellingenId = v.voorspellingenId JOIN (SELECT MAX(voorspellingenId) AS max_voorspellingenId FROM voorspellingen AS v JOIN locaties AS l ON v.locatieId = l.locatieId WHERE l.locatie = %s) AS max_voorspellingen ON v.voorspellingenId = max_voorspellingen.max_voorspellingenId JOIN zWaarden AS z ON vu.zWaarde = z.zWaarde ORDER BY vu.voorspellingUrenId ASC;",
            (locatie,))
        voorspellingen = cursor.fetchall()
        weervoorspelling = []
        for voorspelling in voorspellingen:
            voorspelling['datetime'] = str(voorspelling['datetime'])
            weervoorspelling.append(VoorspellingUren(**voorspelling))
        return weervoorspelling
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij get-request /voorspellinguren/{locatie}.", e)
    finally:
        connection.close()


@app.post('/voorspellingen')
def create_voorspelling(nieuwe_voorspelling: Voorspelling, key: str = Depends(verify_api_key)) -> Voorspelling:
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
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het post-request /voorspellingen, {nieuwe_voorspelling.locatie}, {nieuwe_voorspelling.datetime}", e)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.post('/voorspellinguren')
def create_voorspelling_uren_batch(nieuwe_voorspellingen: List[VoorspellingUren], key: str = Depends(verify_api_key)) -> List[VoorspellingUren]:
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
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het post-request /voorspellinguren.", e)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(locatie: str, key: str = Depends(verify_api_key)):
    '''Verwijderen van voorspellingen en voorspellinguren behalve de meest recente.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()[0]
        print(locatieId)
        cursor.execute("SELECT COUNT(*) FROM voorspellingen WHERE locatieId = %s", (locatieId,))
        count = cursor.fetchone()[0]
        if count == 0:
            logging.warning(f"[API] 200 ACCEPTED: 404: Er zijn geen voorspellingen voor {locatie}.")
            return {"detail": f"Er zijn geen voorspellingen voor {locatie}."}
        cursor.execute(
            "SELECT voorspellingenId FROM voorspellingen WHERE locatieId = %s ORDER BY datetime DESC LIMIT 1",
            (locatieId,))
        latest_prediction_id = cursor.fetchone()[0]
        cursor.execute("SELECT voorspellingenId FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s",
                       (latest_prediction_id, locatieId))
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM voorspellinguren WHERE voorspellingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s",
                       (latest_prediction_id, locatieId))
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het delete-request /voorspellingen/{locatie}.", e)
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()


########################################################################################################################
# LOCATIES ENDPOINTS

@app.get('/locaties')
def get_locaties() -> List[Locatie]:
    '''Haal alle locaties op uit de database en converteer ze naar een lijst van Locatie objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM locaties ORDER BY locatie ASC;")
        locaties = cursor.fetchall()
        locatie = []
        for loc in locaties:
            locatie.append(Locatie(**loc))
        return locatie
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij get-request /locaties.", e)
    finally:
        connection.close()


@app.post('/locaties')
def create_locatie(nieuwe_locatie: Locatie, key: str = Depends(verify_api_key)) -> Locatie:
    '''Voeg een nieuwe locatie toe aan de database en retourneer een Locatie object.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO locaties (locatie) "
            "VALUES (%s)",
            (nieuwe_locatie.locatie,)
        )
        connection.commit()
        return {
            **nieuwe_locatie.dict()
        }
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het post-request /locaties, {nieuwe_locatie.locatie}.", e)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/locaties/{locatie}")
def delete_locatie(locatie: str, key: str = Depends(verify_api_key)):
    '''Verwijder een locatie uit de database.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT COUNT(*) FROM locaties WHERE locatie = %s", (locatie,))
        locatie_count = cursor.fetchone()[0]
        if locatie_count > 0:
            cursor.execute(
                "DELETE FROM metinguren WHERE metingenId IN (SELECT metingenId FROM metingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s))",
                (locatie,))
            cursor.execute("DELETE FROM metingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s)",
                           (locatie,))
            cursor.execute(
                "DELETE FROM voorspellinguren WHERE voorspellingenId IN (SELECT voorspellingenId FROM voorspellingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s))",
                (locatie,))
            cursor.execute(
                "DELETE FROM voorspellingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s)",
                (locatie,))
            cursor.execute("DELETE FROM locaties WHERE locatie = %s", (locatie,))
            connection.commit()
            return {"detail": f"Locatie {locatie} is verwijderd."}
        else:
            logging.warning(f"[API] 200 ACCEPTED: 404: Locatie {locatie} bestaat niet.")
            return {"detail": f"Locatie {locatie} bestaat niet."}
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij het delete-request /locaties/{locatie}.", e)
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()

@app.get('/images/{image}')
def get_images(image: str) -> Image:
    '''Haal alle images op uit de database en converteer ze naar een lijst van Image objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM images where imageId = {image};")
        image = cursor.fetchone()

        return image
    except Exception as e:
        connection.close()
        logging.error(f"[API] %s: Er is een fout opgetreden bij get-request /images.", e)
    finally:
        connection.close()