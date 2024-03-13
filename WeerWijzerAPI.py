from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import DB

app = FastAPI()

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

def metinguren_uit_database_halens():
    '''Haal metingen uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM metinguren WHERE metingenId = (SELECT MAX(m2.metingenId) FROM metinguren m2) ORDER BY metingUrenId ASC;")
        metingen = cursor.fetchall()
        return metingen
    finally:
        connection.close()

# ALLE ENDPOINTS
########################################################################################################################
# METINGEN / METINGUREN ENDPOINTS
@app.get('/metinguren', response_model=List[WeerMetingUren])
def get_metingen():
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    metingen = metinguren_uit_database_halens()
    weermetingen = []
    for meting in metingen:
        meting['datetime'] = str(meting['datetime'])
        weermetingen.append(WeerMetingUren(**meting))
    return weermetingen

@app.post('/metingen', response_model=WeerMeting)
def create_meting(nieuwe_meting: WeerMeting):
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
        nieuwe_meting_id = cursor.lastrowid
        return {
            "metingId": nieuwe_meting_id,
            **nieuwe_meting.dict()
        }
    finally:
        connection.close()
        raise HTTPException(status_code=201)


@app.post('/metinguren', response_model=List[WeerMetingUren])
def create_meting_uren_batch(nieuwe_metingen: List[WeerMetingUren]):
    '''Voeg nieuwe metingen toe aan de database en retourneer een lijst met NieuweWeerMetingUren objecten.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        metingen_values = []
        for meting in nieuwe_metingen:  # <-- Hier aangepast naar nieuwe_metingen
            metingen_values.append((
                meting.datetime, meting.temperature, meting.pressure, meting.winddirection
            ))
        cursor.executemany(
            "INSERT INTO metinguren (metingenId, datetime, temperature, pressure, winddirection) "
            f"VALUES ((SELECT metingenId FROM metingen ORDER BY metingenId DESC LIMIT 1), %s, %s, %s, %s)",
            metingen_values
        )
        connection.commit()
    finally:
        connection.close()
        raise HTTPException(status_code=201)

@app.delete("/deletemetingen")
def delete_metingen():
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM metingen")
        count = cursor.fetchone()[0]
        if count <= 1:
            raise HTTPException(status_code=400, detail="Metingen verwijderen is niet mogelijk: Er is maar één meting opgeslagen.")
        cursor.execute("SELECT metingenId FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR")
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute("DELETE FROM metinguren WHERE metingenId = %s", (measurement_id,))
        cursor.execute("DELETE FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR")
        connection.commit()
        return {"detail": f"{len(old_measurement_ids)} metingen zijn verwijderd."}
    finally:
        connection.close()
        raise HTTPException(status_code=202)