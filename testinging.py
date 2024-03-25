from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import select, asc, func, column, insert
from sqlalchemy.orm import Session
import DB
from DB_new import get_db, MetingUren, Metingen, Locaties, Voorspellingen, VoorspellingUren

app = FastAPI()     # command to start: uvicorn WeerWijzerAPI:app --reload

# CORS-instellingen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeerMetingItem(BaseModel):
    '''Klasse voor het aanmaken van een NieuweWeerMeting object.'''
    locatie: str
    datetime: str


class WeerMetingUrenItem(BaseModel):
    '''Klasse voor het aanmaken van een WeerMeting object.'''
    datetime: str
    temperature: float
    pressure: float
    winddirection: float


class LocatieItem(BaseModel):
    '''Klasse voor het aanmaken van een Locatie object.'''
    locatieId: int
    locatie: str


class VoorspellingItem(BaseModel):
    '''Klasse voor het aanmaken van een Verwachting object.'''
    locatie: str
    datetime: str


class VoorspellingUrenItem(BaseModel):
    '''Klasse voor het aanmaken van een VerwachtingUren object.'''
    datetime: str
    temperature: float
    zWaarde: int

def metinguren_uit_database_halen(locatie):
    '''Haal metingen uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    session = next(get_db())
    stmt = select(MetingUren).join(Metingen, MetingUren.metingenId == Metingen.metingenId).where(Metingen.locatieId == select(Locaties.locatieId).where(Locaties.locatie == locatie), Metingen.metingenId == select(func.max(Metingen.metingenId))).order_by(asc(MetingUren.metingUrenId))
    metingen = session.execute(stmt).all()
    metingen_lst = []
    for i in metingen:
        for j in i:
            metingen_lst.append({'metingUrenId':j.metingUrenId, 'metingenId':j.metingenId, 'datetime': j.datetime, 'temperature':j.temperature, 'pressure': j.pressure, 'winddirection':j.winddirection})
    return metingen_lst

# ALLE ENDPOINTS
########################################################################################################################
# METINGEN / METINGUREN ENDPOINTS
@app.get('/metinguren/{locatie}', response_model=List[WeerMetingUrenItem])
def get_metingen(locatie: str):
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    metingen = uren_uit_database_halens('meting', locatie)
    weermetingen = []
    for meting in metingen:
        meting['datetime'] = str(meting['datetime'])
        weermetingen.append(WeerMetingUrenItem(**meting))
    return weermetingen


@app.post('/metingen', response_model=WeerMetingItem)
def create_meting(nieuwe_meting: WeerMetingItem):
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


@app.post('/metinguren', response_model=List[WeerMetingUrenItem])
def create_meting_uren_batch(nieuwe_metingen: List[WeerMetingUrenItem]):
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

@app.delete("/metingen/{locatie}")
def delete_metingen(locatie: str):
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM metingen WHERE locatieId = %s", (locatieId,))
        count = cursor.fetchone()[0]
        if count <= 1:
            raise HTTPException(status_code=400, detail="Metingen verwijderen is niet mogelijk: Er is maar één meting opgeslagen.")
        cursor.execute("SELECT metingenId FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s", (locatieId,))
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM metinguren WHERE metingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s", (locatieId,))
        connection.commit()
        return {"detail": f"{len(old_measurement_ids)} metingen zijn verwijderd."}
    except Exception:
        connection.close()
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=202)


########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get('/voorspellinguren/{locatie}', response_model=List[VoorspellingUrenItem])
def get_voorspellingen(locatie: str):
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van voorspellinguren objecten.'''
    voorspellingen = uren_uit_database_halens('voorspelling', locatie)
    weervoorspelling = []
    for voorspelling in voorspellingen:
        voorspelling['datetime'] = str(voorspelling['datetime'])
        weervoorspelling.append(VoorspellingUrenItem(**voorspelling))
    return weervoorspelling

@app.post('/voorspellingen', response_model=VoorspellingItem)
def create_voorspelling(nieuwe_voorspelling: VoorspellingItem):
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

@app.post('/voorspellinguren', response_model=List[VoorspellingUrenItem])
def create_voorspelling_uren_batch(nieuwe_voorspellingen: List[VoorspellingUrenItem]):
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

@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(locatie: str):
    '''Verwijderen van voorspellingen en voorspellinguren behalve de meest recente.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()[0]
        print(locatieId)
        cursor.execute("SELECT voorspellingenId FROM voorspellingen WHERE locatieId = %s ORDER BY datetime DESC LIMIT 1", (locatieId,))
        latest_prediction_id = cursor.fetchone()[0]
        cursor.execute("SELECT voorspellingenId FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s", (latest_prediction_id, locatieId))
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM voorspellinguren WHERE voorspellingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s", (latest_prediction_id, locatieId))
        connection.commit()
        return {"detail": f"{len(old_measurement_ids)} voorspellingen zijn verwijderd voor {locatie}."}
    except Exception:
        connection.close()
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=202)