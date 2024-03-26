from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import func, text
from logfiles.log import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from DB import SessionLocal, engine, Base
from DB import (
    DBLocaties,
    DBMetingen,
    DBMetingUren,
    DBVoorspellingen,
    DBVoorspellingUren,
    DBzWaarden,
)

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")


# command to start: uvicorn WeerWijzerAPI:app --reload


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def init_db():
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # seed_db()


# def seed_db():
#     print("Seeding DB")
#     try:
#         db = SessionLocal()
#         if db.bind.url.drivername != "sqlite":
#             db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
#         datumNu = datetime.now() - timedelta(hours=12)

#         # Check if the tables are empty and seed data if they are
#         if db.query(DBMetingen).count() == 0:
#             metingen = [
#                 DBMetingen(metingenId=1, locatieId=1, datetime=datumNu),
#                 DBMetingen(metingenId=2, locatieId=2, datetime=datumNu),
#             ]
#             db.add_all(metingen)
#         if db.query(DBMetingUren).count() == 0:
#             metingUren = [
#                 DBMetingUren(
#                     metingUrenId=1,
#                     metingenId=1,
#                     datetime=datumNu,
#                     temperature=12,
#                     pressure=1008,
#                     winddirection=180,
#                 ),
#                 DBMetingUren(
#                     metingUrenId=2,
#                     metingenId=2,
#                     datetime=datumNu,
#                     temperature=10,
#                     pressure=1003,
#                     winddirection=200,
#                 ),
#             ]
#             db.add_all(metingUren)
#         if db.query(DBLocaties).count() == 0:
#             locaties = [
#                 DBLocaties(locatieId=1, locatie="Apeldoorn"),
#                 DBLocaties(locatieId=2, locatie="Amersfoort"),
#             ]
#             db.add_all(locaties)
#         if db.query(DBVoorspellingen).count() == 0:
#             voorspellingen = [
#                 DBVoorspellingen(voorspellingenId=1, locatieId=1, datetime=datumNu),
#                 DBVoorspellingen(voorspellingenId=2, locatieId=2, datetime=datumNu),
#             ]
#             db.add_all(voorspellingen)
#         if db.query(DBVoorspellingUren).count() == 0:
#             voorspellingUren = [
#                 DBVoorspellingUren(
#                     voorspellingUrenId=1,
#                     voorspellingenId=1,
#                     zWaarde=15,
#                     datetime=datumNu,
#                     temperature=12,
#                 ),
#                 DBVoorspellingUren(
#                     voorspellingUrenId=2,
#                     voorspellingenId=2,
#                     zWaarde=15,
#                     datetime=datumNu,
#                     temperature=10,
#                 ),
#             ]
#             db.add_all(voorspellingUren)
#     except SQLAlchemyError as e:
#         db.rollback()
#         logging.error(f"Er is een fout opgetreden bij het seeden van de database: {e}")
#         return e
#     finally:
#         db.commit()
#         if db.bind.url.drivername != "sqlite":
#             db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
#         db.close()


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
    """Klasse voor het aanmaken van een NieuweWeerMeting object."""

    locatie: str
    datetime: datetime


class WeerMetingUren(BaseModel):
    """Klasse voor het aanmaken van een WeerMeting object."""

    # metingenId: int
    datetime: datetime
    temperature: float
    pressure: float
    winddirection: float


class Locatie(BaseModel):
    """Klasse voor het aanmaken van een Locatie object."""

    locatieId: int
    locatie: str


class Voorspelling(BaseModel):
    """Klasse voor het aanmaken van een Verwachting object."""

    locatie: str
    datetime: datetime


class VoorspellingUren(BaseModel):
    """Klasse voor het aanmaken van een VerwachtingUren object."""

    # voorspellingenId: int
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
@app.get("/metinguren/{locatie}", response_model=List[WeerMetingUren])
def get_metingen(locatie: str, db: Session = Depends(get_db)):
    """Haal de meest recente meting op uit de database en converteer deze naar een lijst van WeerMeting objecten."""
    try:
        locatie_db = db.query(DBLocaties).filter(DBLocaties.locatie == locatie).first()
        if not locatie_db:
            return {"detail": f"Locatie {locatie} bestaat niet in de database."}

        # Haal de meest recente meting op
        recentste_meting = (
            db.query(DBMetingen)
            .filter(DBMetingen.locatieId == locatie_db.locatieId)
            .order_by(DBMetingen.datetime.desc())
            .first()
        )
        if not recentste_meting:
            return {"detail": f"Geen metingen gevonden voor locatie {locatie}."}

        # Haal de metinguren op die geassocieerd zijn met de meest recente meting
        metinguren = (
            db.query(DBMetingUren)
            .filter(DBMetingUren.metingenId == recentste_meting.metingenId)
            .all()
        )
        return metinguren
    except SQLAlchemyError as e:
        logging.error(
            f"[API] Er is een fout opgetreden bij get-request metinguren/{locatie}: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post("/metingen", response_model=WeerMeting)
def create_meting(
    nieuwe_meting: WeerMeting,
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg een nieuwe meting toe aan de database en retourneer een NieuweWeerMeting object."""
    try:
        locatie_db = (
            db.query(DBLocaties)
            .filter(DBLocaties.locatie == nieuwe_meting.locatie)
            .first()
        )
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        meting_db = DBMetingen(
            locatieId=locatie_db.locatieId, datetime=nieuwe_meting.datetime
        )
        db.add(meting_db)
        db.commit()
        return nieuwe_meting
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het toevoegen van een nieuwe meting: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post("/metinguren", response_model=List[WeerMetingUren])
def create_meting_uren_batch(
    nieuwe_metingen: List[WeerMetingUren],
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg nieuwe metingen toe aan de database en retourneer een lijst met NieuweWeerMetingUren objecten."""
    try:
        # Haal de maximale metingenId op
        max_metingen_id = db.query(func.max(DBMetingen.metingenId)).scalar()
        if not max_metingen_id:
            raise HTTPException(status_code=404, detail="Geen metingen gevonden")

        for meting in nieuwe_metingen:
            meting_uren_db = DBMetingUren(
                metingenId=max_metingen_id,
                datetime=meting.datetime,
                temperature=meting.temperature,
                pressure=meting.pressure,
                winddirection=meting.winddirection,
            )
            db.add(meting_uren_db)
        db.commit()
        return nieuwe_metingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het toevoegen van nieuwe metinguren: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/metingen/{locatie}")
def delete_metingen(
    locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)
):
    """Verwijder metingen en metinguren ouder dan 12 uur."""
    try:
        locatie_db = db.query(DBLocaties).filter(DBLocaties.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        # Zoek de metingen ouder dan 12 uur
        cutoff_time = datetime.utcnow() - timedelta(hours=12)
        metingen_ouder_dan_12_uur = (
            db.query(DBMetingen)
            .join(DBLocaties)
            .filter(DBLocaties.locatie == locatie, DBMetingen.datetime < cutoff_time)
            .all()
        )

        # Controleer of er meer dan één meting is
        totaal_metingen = (
            db.query(DBMetingen)
            .join(DBLocaties)
            .filter(DBLocaties.locatie == locatie)
            .count()
        )
        if totaal_metingen <= 1:
            return {
                "detail": f"Er is slechts één / null meting voor locatie {locatie}. Deze wordt niet verwijderd."
            }

        # Verwijder de metingen en metinguren ouder dan 12 uur
        for meting in metingen_ouder_dan_12_uur:
            # Verwijder eerst de gerelateerde metinguren
            for meting_uren in meting.metinguren:
                db.delete(meting_uren)
            db.delete(meting)
        db.commit()

        return {
            "detail": f"Metingen ouder dan 12 uur voor locatie {locatie} zijn verwijderd."
        }
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het delete-request /metingen/{locatie}: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get("/voorspellinguren/{locatie}", response_model=List[VoorspellingUren])
def get_voorspellingen(locatie: str, db: Session = Depends(get_db)):
    """Haal de meest recente voorspelling op uit de database en converteer deze naar een lijst van VoorspellingUren objecten."""
    try:
        locatie_db = db.query(DBLocaties).filter(DBLocaties.locatie == locatie).first()
        if not locatie_db:
            return {"detail": f"Locatie {locatie} bestaat niet in de database."}

        # Haal de meest recente voorspelling op
        recentste_voorspelling = (
            db.query(DBVoorspellingen)
            .filter(DBVoorspellingen.locatieId == locatie_db.locatieId)
            .order_by(DBVoorspellingen.datetime.desc())
            .first()
        )
        if not recentste_voorspelling:
            return {"detail": f"Geen voorspellingen gevonden voor locatie {locatie}."}

        # Haal de voorspellinguren op die geassocieerd zijn met de meest recente voorspelling
        voorspellinguren = (
            db.query(DBVoorspellingUren)
            .filter(
                DBVoorspellingUren.voorspellingenId
                == recentste_voorspelling.voorspellingenId
            )
            .all()
        )

        # Maak een nieuwe lijst van voorspellinguren
        nieuwe_voorspellinguren = []
        for voorspellinguur in voorspellinguren:
            beschrijving = (
                db.query(DBzWaarden.beschrijving)
                .filter(DBzWaarden.zWaarde == voorspellinguur.zWaarde)
                .scalar()
            )
            nieuwe_voorspellinguren.append(
                {
                    "datetime": voorspellinguur.datetime,
                    "temperature": voorspellinguur.temperature,
                    "zWaarde": voorspellinguur.zWaarde,
                    "beschrijving": beschrijving,
                    "sneeuw": True if voorspellinguur.temperature <= -5 else False,
                }
            )

        return nieuwe_voorspellinguren
    except SQLAlchemyError as e:
        logging.error(
            f"[API] Er is een fout opgetreden bij get-request voorspellinguren/{locatie}: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post("/voorspellingen", response_model=Voorspelling)
def create_voorspelling(
    nieuwe_voorspelling: Voorspelling,
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg een nieuwe voorspelling toe aan de database en retourneer een NieuweVoorspelling object."""
    try:
        locatie_db = (
            db.query(DBLocaties)
            .filter(DBLocaties.locatie == nieuwe_voorspelling.locatie)
            .first()
        )
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        voorspelling_db = DBVoorspellingen(
            locatieId=locatie_db.locatieId, datetime=nieuwe_voorspelling.datetime
        )
        db.add(voorspelling_db)
        db.commit()
        return nieuwe_voorspelling
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het post-request /voorspellingen: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post("/voorspellinguren", response_model=List[VoorspellingUren])
def create_voorspelling_uren_batch(
    nieuwe_voorspellingen: List[VoorspellingUren],
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg nieuwe voorspellingen toe aan de database en retourneer een lijst met NieuweVoorspellingUren objecten."""
    try:
        # Haal de maximale voorspellingenId op
        max_voorspellingen_id = db.query(
            func.max(DBVoorspellingen.voorspellingenId)
        ).scalar()
        if not max_voorspellingen_id:
            raise HTTPException(status_code=404, detail="Geen voorspellingen gevonden")

        for voorspelling in nieuwe_voorspellingen:
            voorspelling_uren_db = DBVoorspellingUren(
                voorspellingenId=max_voorspellingen_id,
                datetime=voorspelling.datetime,
                temperature=voorspelling.temperature,
                zWaarde=voorspelling.zWaarde,
            )
            db.add(voorspelling_uren_db)
        db.commit()
        return nieuwe_voorspellingen
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het post-request /voorspellinguren: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(
    locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)
):
    """Verwijderen van voorspellingen behalve de meest recente."""
    try:
        locatie_db = db.query(DBLocaties).filter(DBLocaties.locatie == locatie).first()
        if not locatie_db:
            raise HTTPException(status_code=404, detail="Locatie niet gevonden")

        # Zoek de meest recente voorspelling
        meest_recente_voorspelling = (
            db.query(DBVoorspellingen)
            .join(DBLocaties)
            .filter(DBLocaties.locatie == locatie)
            .order_by(DBVoorspellingen.voorspellingenId.desc())
            .first()
        )

        # Verwijder alle voorspellingen behalve de meest recente
        voorspellingen_te_verwijderen = (
            db.query(DBVoorspellingen)
            .join(DBLocaties)
            .filter(
                DBLocaties.locatie == locatie,
                DBVoorspellingen.voorspellingenId
                != meest_recente_voorspelling.voorspellingenId,
            )
            .all()
        )
        for voorspelling in voorspellingen_te_verwijderen:
            # Verwijder eerst de gerelateerde voorspellinguren
            for voorspelling_uren in voorspelling.voorspellinguren:
                db.delete(voorspelling_uren)
            db.delete(voorspelling)
        db.commit()

        return {
            "detail": f"Alle voorspellingen voor locatie {locatie} zijn verwijderd, behalve de meest recente."
        }
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het delete-request /voorspellingen/{locatie}: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


########################################################################################################################
# LOCATIES ENDPOINTS
@app.get("/locaties", response_model=List[Locatie])
def get_locaties(db: Session = Depends(get_db)):
    """Haal alle locaties op uit de database en converteer ze naar een lijst van Locatie objecten."""
    try:
        locaties = db.query(DBLocaties).all()
        return locaties
    except SQLAlchemyError as e:
        logging.error(f"[API] Er is een fout opgetreden bij get-request /locaties: {e}")
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.post("/locaties", response_model=Locatie)
def create_locatie(
    nieuwe_locatie: Locatie,
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg een nieuwe locatie toe aan de database en retourneer een Locatie object."""
    try:
        locatie_db = DBLocaties(**nieuwe_locatie.dict())
        db.add(locatie_db)
        db.commit()
        return nieuwe_locatie
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(
            f"[API] Er is een fout opgetreden bij het post-request /locaties: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")


@app.delete("/locaties/{locatie}")
def delete_locatie(
    locatie: str, db: Session = Depends(get_db), key: str = Depends(verify_api_key)
):
    """Verwijder een locatie uit de database."""
    try:
        locatie_db = db.query(DBLocaties).filter(DBLocaties.locatie == locatie).first()
        if not locatie_db:
            return {"detail": f"Locatie {locatie} bestaat niet in de database."}

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
        logging.error(
            f"[API] Er is een fout opgetreden bij het delete-request /locaties/{locatie}: {e}"
        )
        raise HTTPException(status_code=500, detail="Interne serverfout")
