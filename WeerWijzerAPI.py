from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import func
from logfiles.log import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from DB import SessionLocal, engine, init_db
from DB import Locatie as DBLocatie, Meting as DBMeting, MetingUren as DBMetingUren, Voorspelling as DBVoorspelling, \
    VoorspellingUren as DBVoorspellingUren, zWaarden as DBzWaarden

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

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
    # metingenId: int
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
    # voorspellingenId: int
    datetime: datetime
    temperature: float
    zWaarde: int
    beschrijving: Optional[str] = None
    sneeuw: Optional[bool] = None


class zWaarden(BaseModel):
    '''Klasse voor het aanmaken van een zWaarden object.'''
    zWaarde: int
    beschrijving: str


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
    '''Haal de meest recente meting op uit de database en converteer deze naar een lijst van WeerMeting objecten.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail=f"Locatie {locatie} bestaat niet in de database.")

        # Haal de meest recente meting op
        recentste_meting = db.query(DBMeting).filter(DBMeting.locatieId == locatie_db.locatieId).order_by(
            DBMeting.datetime.desc()).first()
        if not recentste_meting:
            raise HTTPException(status_code=404, detail=f"Geen metingen gevonden voor locatie {locatie}.")

        # Haal de metinguren op die geassocieerd zijn met de meest recente meting
        metinguren = db.query(DBMetingUren).filter(DBMetingUren.metingenId == recentste_meting.metingenId).all()
        return metinguren
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
        # Haal de maximale metingenId op
        max_metingen_id = db.query(func.max(DBMeting.metingenId)).scalar()
        if not max_metingen_id:
            raise HTTPException(status_code=404, detail="Geen metingen gevonden")

        metingen_toe_te_voegen = []
        for meting in nieuwe_metingen:
            metingen_toe_te_voegen.append({
                "metingenId": max_metingen_id,
                "datetime": meting.datetime,
                "temperature": meting.temperature,
                "pressure": meting.pressure,
                "winddirection": meting.winddirection
            })

        # Voer de batch-insert uit
        db.execute(DBMetingUren.__table__.insert(), metingen_toe_te_voegen)
        db.commit()
        return nieuwe_metingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het toevoegen van nieuwe metinguren: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


# METINGEN DELETE-ENDPOINT
@app.delete("/metingen/{locatie}")
def delete_metingen(locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Verwijder metingen en metinguren ouder dan 12 uur.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail=f"Locatie {locatie} bestaat niet in de database.")

        # Zoek de metingen ouder dan 12 uur
        cutoff_time = datetime.utcnow() - timedelta(hours=12)
        metingen_to_delete = db.query(DBMeting).join(DBLocatie).filter(
            DBLocatie.locatie == locatie, DBMeting.datetime < cutoff_time).all()

        # Controleer of er meer dan één meting is
        total_metingen = len(metingen_to_delete)
        if total_metingen <= 1:
            raise HTTPException(status_code=403, detail=f"Er is slechts één / geen meting voor locatie {locatie}. Deze wordt niet verwijderd.")

        # Verwijder de metingen ouder dan 12 uur
        for meting in metingen_to_delete:
            db.query(DBMetingUren).filter(DBMetingUren.metingenId == meting.metingenId).delete(
                synchronize_session=False)
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
    '''Haal de meest recente voorspelling op uit de database en converteer deze naar een lijst van VoorspellingUren objecten.'''
    try:
        # Voer een JOIN-query uit om de benodigde informatie op te halen
        voorspellinguren = db.query(DBVoorspellingUren, DBzWaarden.beschrijving) \
            .join(DBVoorspelling, DBVoorspelling.voorspellingenId == DBVoorspellingUren.voorspellingenId) \
            .join(DBzWaarden, DBVoorspellingUren.zWaarde == DBzWaarden.zWaarde) \
            .join(DBLocatie, DBVoorspelling.locatieId == DBLocatie.locatieId) \
            .filter(DBLocatie.locatie == locatie) \
            .order_by(DBVoorspelling.datetime.desc()) \
            .all()

        if not voorspellinguren:
            raise HTTPException(status_code=404, detail=f"Geen voorspellingen gevonden voor locatie {locatie}.")

        # Maak een lijst van dictionaries voor de voorspellinguren
        nieuwe_voorspellinguren = []
        for voorspellinguur, beschrijving in voorspellinguren:
            nieuwe_voorspellinguren.append({
                "datetime": voorspellinguur.datetime,
                "temperature": voorspellinguur.temperature,
                "zWaarde": voorspellinguur.zWaarde,
                "beschrijving": beschrijving,
                "sneeuw": True if voorspellinguur.temperature <= -5 else False
            })

        return nieuwe_voorspellinguren
    except SQLAlchemyError as e:
        logging.error(f"[API] Er is een fout opgetreden bij get-request voorspellinguren/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post('/voorspellingen', response_model=Voorspelling)
def create_voorspelling(nieuwe_voorspelling: Voorspelling, db: Session = Depends(get_db),
                        key: str = Depends(verify_api_key)):
    '''Voeg een nieuwe voorspelling toe aan de database en retourneer een NieuweVoorspelling object.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == nieuwe_voorspelling.locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        voorspelling_db = DBVoorspelling(locatieId=locatie_db.locatieId, datetime=nieuwe_voorspelling.datetime)
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
        # Haal de maximale voorspellingenId op
        max_voorspellingen_id = db.query(func.max(DBVoorspelling.voorspellingenId)).scalar()
        if not max_voorspellingen_id:
            raise HTTPException(status_code=404, detail="Geen voorspellingen gevonden")

        # Maak een lijst van voorspellingen voor batch-insert
        voorspellingen_toe_te_voegen = []
        for voorspelling in nieuwe_voorspellingen:
            voorspellingen_toe_te_voegen.append({
                "voorspellingenId": max_voorspellingen_id,
                "datetime": voorspelling.datetime,
                "temperature": voorspelling.temperature,
                "zWaarde": voorspelling.zWaarde
            })

        # Voer de batch-insert uit
        db.execute(DBVoorspellingUren.__table__.insert(), voorspellingen_toe_te_voegen)
        db.commit()

        return nieuwe_voorspellingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het toevoegen van nieuwe voorspellinguren: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)):
    '''Verwijderen van voorspellingen behalve de meest recente.'''
    try:
        locatie_db = db.query(DBLocatie).filter(DBLocatie.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail=f"Locatie {locatie} bestaat niet in de database.")

        # Zoek de meest recente voorspelling
        meest_recente_voorspelling = db.query(DBVoorspelling).join(DBLocatie).filter(
            DBLocatie.locatie == locatie).order_by(DBVoorspelling.voorspellingenId.desc()).first()

        # Verwijder alle voorspellingen behalve de meest recente
        db.query(DBVoorspellingUren).filter(DBVoorspellingUren.voorspellingenId.in_(
            db.query(DBVoorspelling.voorspellingenId).join(DBLocatie).filter(DBLocatie.locatie == locatie,
                                                                             DBVoorspelling.voorspellingenId != meest_recente_voorspelling.voorspellingenId)
        )).delete(synchronize_session=False)

        db.query(DBVoorspelling).filter(DBVoorspelling.locatieId == locatie_db.locatieId,
                                        DBVoorspelling.voorspellingenId != meest_recente_voorspelling.voorspellingenId).delete(
            synchronize_session=False)

        db.commit()

        return {"detail": f"Alle voorspellingen voor locatie {locatie} zijn verwijderd, behalve de meest recente."}
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
            raise HTTPException(status_code=404, detail=f"Locatie {locatie} bestaat niet in de database.")

        # Verwijder eerst de gerelateerde metingen, metinguren, voorspellingen en voorspellinguren
        for meting in locatie_db.metingen:
            for meting_uren in meting.metinguren:
                db.delete(meting_uren)
            db.delete(meting)
        for voorspelling in locatie_db.voorspellingen:
            for voorspelling_uren in voorspelling.voorspellinguren:
                db.delete(voorspelling_uren)
            db.delete(voorspelling)

        db.delete(locatie_db)
        db.commit()
        return {"detail": f"Locatie {locatie} is verwijderd."}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[API] Er is een fout opgetreden bij het delete-request /locaties/{locatie}: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")