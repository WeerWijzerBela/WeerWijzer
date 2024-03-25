from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import DB
from logfiles.log import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from DB import SessionLocal, engine
from DB import Locatie as DBLocatie, Meting as DBMeting, MetingUren as DBMetingUren, Voorspelling as DBVoorspelling, VoorspellingUren as DBVoorspellingUren

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WeerMeting(BaseModel):
    '''Klasse voor het aanmaken van een NieuweWeerMeting object.'''
    locatie: str
    datetime: datetime


class WeerMetingUren(BaseModel):
    '''Klasse voor het aanmaken van een WeerMeting object.'''
    metingenId: Optional[int] = None
    datetime: datetime
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
    datetime: datetime


class VoorspellingUren(BaseModel):
    '''Klasse voor het aanmaken van een VerwachtingUren object.'''
    datetime: datetime
    temperature: float
    zWaarde: int
    beschrijving: Optional[str] = None
    sneeuw: Optional[bool] = None


def verify_api_key(api_key: str = None):
    if api_key is None or api_key != API_KEY:
        logging.warning("[API] 403: Request met een ongeldige API-sleutel.")
        raise HTTPException(status_code=403, detail="Ongeldige API-sleutel")
    return True


# ALLE ENDPOINTS
########################################################################################################################
# METINGEN / METINGUREN ENDPOINTS
@app.get('/metinguren/{locatie}', response_model=List[WeerMetingUren])
def get_metingen(locatie: str, db: Session = Depends(get_db)):
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            return {"detail": f"Locatie {locatie} bestaat niet in de database."}
        metingen = db.query(DBMetingUren).join(DBMeting).filter(DBMeting.locatieId == locatie_db.locatieId).all()
        return metingen
    except SQLAlchemyError as e:
        logging.error(f"[API] Er is een fout opgetreden bij get-request metinguren/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")

@app.post('/metingen', response_model=WeerMeting)
def create_meting(nieuwe_meting: WeerMeting, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Voeg een nieuwe meting toe aan de database en retourneer een NieuweWeerMeting object.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == nieuwe_meting.locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        meting_db = DBMeting(locatieId=locatie_db.locatieId, datetime=nieuwe_meting.datetime)
        db.add(meting_db)
        db.commit()
        return nieuwe_meting
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het toevoegen van een nieuwe meting: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post('/metinguren', response_model=List[WeerMetingUren])
def create_meting_uren_batch(nieuwe_metingen: List[WeerMetingUren], db: Session = Depends(get_db),
                             key: str = Depends(verify_api_key)):
    '''Voeg nieuwe metingen toe aan de database en retourneer een lijst met NieuweWeerMetingUren objecten.'''
    try:
        for meting in nieuwe_metingen:
            meting_db = db.query(DBMeting).filter(DBMeting.metingenId == meting.metingenId).first()
            if not meting_db:
                raise HTTPException(status_code=404, detail="Meting niet gevonden")

            locatie_db = db.query(DBLocatie).filter(DBLocatie.locatieId == meting_db.locatieId).first()
            if not locatie_db:
                raise HTTPException(status_code=404, detail="Locatie niet gevonden")

            meting_uren_db = DBMetingUren(metingenId=meting_db.metingenId, datetime=meting.datetime, temperature=meting.temperature, pressure=meting.pressure, winddirection=meting.winddirection)
            db.add(meting_uren_db)
        db.commit()
        return nieuwe_metingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het toevoegen van nieuwe metinguren: {e}")
        #raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/metingen/{locatie}")
def delete_metingen(locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        # Zoek de metingen ouder dan 12 uur
        cutoff_time = datetime.utcnow() - timedelta(hours=12)
        metingen_ouder_dan_12_uur = db.query(DBMeting).join(Locatie).filter(DBLocatie.locatie == locatie,
                                                                          DBMeting.datetime < cutoff_time).all()

        # Verwijder de metingen en metinguren ouder dan 12 uur
        for meting in metingen_ouder_dan_12_uur:
            db.delete(meting)
        db.commit()

        return {"detail": f"Metingen ouder dan 12 uur voor locatie {locatie} zijn verwijderd."}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het delete-request /metingen/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")

########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get('/voorspellinguren/{locatie}', response_model=List[VoorspellingUren])
def get_voorspellingen(locatie: str, db: Session = Depends(get_db)):
    '''Haal alle metingen op uit de database en converteer ze naar een lijst van voorspellinguren objecten.'''
    try:
        locatie_db = db.query(Locatie).filter(Locatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")
        voorspellingen = db.query(VoorspellingUren).join(Voorspelling).filter(
            Voorspelling.locatieId == locatie_db.locatieId).all()
        return voorspellingen
    except SQLAlchemyError as e:
        logging.error(f"[API] Er is een fout opgetreden bij get-request /voorspellinguren/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post('/voorspellingen', response_model=Voorspelling)
def create_voorspelling(nieuwe_voorspelling: Voorspelling, db: Session = Depends(get_db),
                        key: str = Depends(verify_api_key)):
    '''Voeg een nieuwe voorspelling toe aan de database en retourneer een NieuweVoorspelling object.'''
    try:
        locatie_db = db.query(Locatie).filter(Locatie.locatie == nieuwe_voorspelling.locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        voorspelling_db = Voorspelling(locatieId=locatie_db.locatieId, datetime=nieuwe_voorspelling.datetime)
        db.add(voorspelling_db)
        db.commit()
        return nieuwe_voorspelling
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het post-request /voorspellingen: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post('/voorspellinguren', response_model=List[VoorspellingUren])
def create_voorspelling_uren_batch(nieuwe_voorspellingen: List[VoorspellingUren], db: Session = Depends(get_db),
                                   key: str = Depends(verify_api_key)):
    '''Voeg nieuwe voorspellingen toe aan de database en retourneer een lijst met NieuweVoorspellingUren objecten.'''
    try:
        for voorspelling in nieuwe_voorspellingen:
            locatie_db = db.query(Locatie).filter(Locatie.locatie == voorspelling.locatie).first()
            if not locatie_db:
                raise HTTPException(status_code=404, detail="Locatie niet gevonden")

            voorspelling_db = Voorspelling(locatieId=locatie_db.locatieId, datetime=voorspelling.datetime)
            db.add(voorspelling_db)
        db.commit()
        return nieuwe_voorspellingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het post-request /voorspellinguren: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Verwijderen van voorspellingen en voorspellinguren behalve de meest recente.'''
    try:
        locatie_db = db.query(Locatie).filter(Locatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        # Zoek de voorspellingen ouder dan 12 uur
        cutoff_time = datetime.utcnow() - timedelta(hours=12)
        voorspellingen_ouder_dan_12_uur = db.query(Voorspelling).join(Locatie).filter(Locatie.locatie == locatie,
                                                                                      Voorspelling.datetime < cutoff_time).all()

        # Verwijder de voorspellingen en voorspellinguren ouder dan 12 uur
        for voorspelling in voorspellingen_ouder_dan_12_uur:
            db.delete(voorspelling)
        db.commit()

        return {"detail": f"Voorspellingen ouder dan 12 uur voor locatie {locatie} zijn verwijderd."}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het delete-request /voorspellingen/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


########################################################################################################################
# LOCATIES ENDPOINTS
@app.get('/locaties', response_model=List[Locatie])
def get_locaties(db: Session = Depends(get_db)):
    '''Haal alle locaties op uit de database en converteer ze naar een lijst van Locatie objecten.'''
    try:
        locaties = db.query(DBLocatie).all()
        return locaties
    except SQLAlchemyError as e:
        logging.error(f"[API] Er is een fout opgetreden bij get-request /locaties: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post('/locaties', response_model=Locatie)
def create_locatie(nieuwe_locatie: Locatie, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Voeg een nieuwe locatie toe aan de database en retourneer een Locatie object.'''
    try:
        locatie_db = DBLocatie(**nieuwe_locatie.dict())
        db.add(locatie_db)
        db.commit()
        return nieuwe_locatie
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het post-request /locaties: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/locaties/{locatie}")
def delete_locatie(locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Verwijder een locatie uit de database.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            return {"detail": f"Locatie {locatie} bestaat niet in de database."}
        db.delete(locatie_db)
        db.commit()
        return {"detail": f"Locatie {locatie} is verwijderd."}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het delete-request /locaties/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")
