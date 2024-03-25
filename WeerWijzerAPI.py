from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from logfiles.log import logging
from typing import List, Optional
import hashlib
from sqlalchemy import (
    select,
    asc,
    desc,
    func,
    column,
    insert,
    text,
    Column,
    create_engine,
    Integer,
    DateTime,
    ForeignKey,
    DECIMAL,
    VARCHAR,
    String,
    and_,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    query,
)
from dotenv import load_dotenv
import datetime as dt
import os

load_dotenv()

# API_KEY = os.environ.get("API_KEY")
API_KEY = "test"
DB_URL = f"mysql+mysqlconnector://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}?auth_plugin="
testing_DB_URL = "sqlite:///:memory:"

engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class DBMetingen(Base):
    __tablename__ = "metingen"
    metingenId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    locatieId: Mapped[int] = mapped_column(ForeignKey("locaties.locatieId"))
    datetime: Mapped[dt.datetime] = mapped_column(DateTime)


class DBMetingUren(Base):
    __tablename__ = "metinguren"
    metingUrenId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    metingenId: Mapped[int] = mapped_column(ForeignKey("metingen.metingenId"))
    datetime: Mapped[dt.datetime] = mapped_column(DateTime)
    temperature: Mapped[DECIMAL] = mapped_column(DECIMAL(5, 2))
    pressure: Mapped[DECIMAL] = mapped_column(DECIMAL(6, 2))
    winddirection: Mapped[VARCHAR] = mapped_column(VARCHAR(255))


class DBLocaties(Base):
    __tablename__ = "locaties"
    locatieId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    locatie: Mapped[VARCHAR] = mapped_column(VARCHAR(255))


class DBVoorspellingen(Base):
    __tablename__ = "voorspellingen"
    voorspellingenId: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    locatieId: Mapped[int] = mapped_column(ForeignKey("locaties.locatieId"))
    datetime: Mapped[dt.datetime] = mapped_column(DateTime)


class DBVoorspellingUren(Base):
    __tablename__ = "voorspellinguren"
    voorspellingUrenId: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    voorspellingenId: Mapped[int] = mapped_column(
        ForeignKey("voorspellingen.voorspellingenId")
    )
    datetime: Mapped[dt.datetime] = mapped_column(DateTime)
    temperature: Mapped[DECIMAL] = mapped_column(DECIMAL(5, 2))
    zWaarde: Mapped[int] = mapped_column()


class DBzWaarden(Base):
    __tablename__ = "zWaarden"
    zWaarde: Mapped[int] = mapped_column(primary_key=True)
    beschrijving: Mapped[str] = mapped_column(String(30))


# command to start: uvicorn WeerWijzerAPI:app --reload


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def init_db():
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    seed_db()


def seed_db():
    print("Seeding DB")
    db = SessionLocal()
    if db.bind.url.drivername != "sqlite":
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    datumNu = dt.datetime.now()

    # Check if the tables are empty and seed data if they are
    if db.query(DBMetingen).count() == 0:
        metingen = [
            DBMetingen(metingenId=1, locatieId=1, datetime=datumNu),
            DBMetingen(metingenId=2, locatieId=2, datetime=datumNu),
        ]
        db.add_all(metingen)
    if db.query(DBMetingUren).count() == 0:
        metingUren = [
            DBMetingUren(
                metingUrenId=1,
                metingenId=1,
                datetime=datumNu,
                temperature=12,
                pressure=1008,
                winddirection=180,
            ),
            DBMetingUren(
                metingUrenId=2,
                metingenId=2,
                datetime=datumNu,
                temperature=10,
                pressure=1003,
                winddirection=200,
            ),
        ]
        db.add_all(metingUren)
    if db.query(DBLocaties).count() == 0:
        locaties = [
            DBLocaties(locatieId=1, locatie="Apeldoorn"),
            DBLocaties(locatieId=2, locatie="Amersfoort"),
        ]
        db.add_all(locaties)
    if db.query(DBVoorspellingen).count() == 0:
        voorspellingen = [
            DBVoorspellingen(voorspellingenId=1, locatieId=1, datetime=datumNu),
            DBVoorspellingen(voorspellingenId=2, locatieId=2, datetime=datumNu),
        ]
        db.add_all(voorspellingen)
    if db.query(DBVoorspellingUren).count() == 0:
        voorspellingUren = [
            DBVoorspellingUren(
                voorspellingUrenId=1,
                voorspellingenId=1,
                datetime=datumNu,
                temperature=12,
                zWaarde=15,
            ),
            DBVoorspellingUren(
                voorspellingUrenId=2,
                voorspellingenId=2,
                datetime=datumNu,
                temperature=10,
                zWaarde=15,
            ),
        ]
        db.add_all(voorspellingUren)
    db.commit()
    if db.bind.url.drivername != "sqlite":
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    db.close()


app = FastAPI(lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CORS-instellingen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeerMeting(BaseModel):
    """Klasse voor het aanmaken van een NieuweWeerMeting object."""

    locatie: str
    datetime: dt.datetime


class WeerMetingUren(BaseModel):
    """Klasse voor het aanmaken van een WeerMeting object."""

    datetime: dt.datetime
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
    datetime: str


class VoorspellingUren(BaseModel):
    """Klasse voor het aanmaken van een VerwachtingUren object."""

    datetime: str
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
@app.get("/metinguren/{locatie}")
def get_metingen(locatie: str, db: Session = Depends(get_db)):
    """Haal alle metingen op uit de database en converteer ze naar een lijst van WeerMeting objecten."""
    # try:
    values = {"locatie": locatie}
    query = text(
        "SELECT mu.* FROM metinguren AS mu JOIN metingen AS m ON mu.metingenId = m.metingenId JOIN ( SELECT MAX(metingenId) AS max_metingenId FROM metingen AS m JOIN locaties AS l ON m.locatieId = l.locatieId WHERE l.locatie = :locatie) AS max_metingen ON m.metingenId = max_metingen.max_metingenId ORDER BY mu.metingUrenId ASC;"
    )
    result = db.execute(query, values).scalar()
    return result
    metingen = [dict(row) for row in result]  # Convert result to a list of dictionaries
    return metingen
    return result
    metingen = [dict(row) for row in result]
    weermetingen = []
    for meting in metingen:
        meting["datetime"] = str(meting["datetime"])
        weermetingen.append(WeerMetingUren(**meting))
    return weermetingen
    # except Exception as e:
    #     db.close()
    #     logging.error(
    #         f"[API] %s: Er is een fout opgetreden bij get-request metinguren/{locatie}",
    #         e,
    #     )
    # finally:
    #     db.close()
    # try:
    #     subq = (
    #         select(func.max(DBMetingen.metingenId))
    #         .join(DBLocaties, DBMetingen.locatieId == DBLocaties.locatieId)
    #         .where(DBLocaties.locatie == locatie)
    #     )
    #     query = (
    #         select(DBMetingUren)
    #         .join(DBMetingen, DBMetingUren.metingenId == DBMetingen.metingenId)
    #         .join(DBLocaties, DBMetingen.locatieId == DBLocaties.locatieId)
    #         .where(and_(DBLocaties.locatie == locatie, DBMetingen.metingenId == subq))
    #         .order_by(asc(DBMetingUren.metingUrenId))
    #     )
    #     values = {"locatie": locatie}
    #     query = text(
    #         "SELECT mu.* FROM metinguren AS mu JOIN metingen AS m ON mu.metingenId = m.metingenId JOIN ( SELECT MAX(metingenId) AS max_metingenId FROM metingen AS m JOIN locaties AS l ON m.locatieId = l.locatieId WHERE l.locatie = :locatie) AS max_metingen ON m.metingenId = max_metingen.max_metingenId ORDER BY mu.metingUrenId ASC;"
    #     )
    #     metingen_totaal = db.execute(query, values).all()
    #     weermetingen = []
    #     for i in metingen_totaal:
    #         for j in i:
    #             weermetingen.append(
    #                 WeerMetingUren(
    #                     datetime=j.datetime,
    #                     temperature=j.temperature,
    #                     pressure=j.pressure,
    #                     winddirection=j.winddirection,
    #                 )
    #             )
    #     return weermetingen
    # except Exception as e:
    #     logging.error(
    #         f"[API] %s: Er is een fout opgetreden bij get-request metinguren/{locatie}",
    #         e,
    #     )


@app.post("/metingen", response_model=WeerMeting)
def create_meting(
    nieuwe_meting: WeerMeting,
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg een nieuwe meting toe aan de database en retourneer een NieuweWeerMeting object."""
    try:
        stmt = insert(DBMetingen).values(
            locatieId=select(DBLocaties.locatieId).where(
                DBLocaties.locatie == nieuwe_meting.locatie
            ),
            datetime=nieuwe_meting.datetime,
        )
        db.execute(stmt)
        return {**nieuwe_meting.dict()}
    except Exception as e:
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het toevoegen van een nieuwe meting, {nieuwe_meting.locatie}, {nieuwe_meting.datetime}",
            e,
        )
    finally:
        raise HTTPException(status_code=201)

    # atetime: dt.datetime
    temperature: float
    pressure: float
    winddirection: float


@app.post("/metinguren", response_model=List[WeerMetingUren])
def create_meting_uren_batch(
    nieuwe_metingen: List[WeerMetingUren],
    db: Session = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    """Voeg nieuwe metingen toe aan de database en retourneer een lijst met NieuweWeerMetingUren objecten."""
    try:
        for meting in nieuwe_metingen:
            latest_metingenId = db.execute(
                select(func.max(DBMetingen.metingenId))
            ).scalar()
            stmt = insert(DBMetingUren).values(
                metingenId=latest_metingenId,
                datetime=meting.datetime,
                temperature=meting.temperature,
                pressure=meting.pressure,
                winddirection=meting.winddirection,
            )
            db.execute(stmt)
    except Exception as e:
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het toevoegen van nieuwe metinguren.",
            e,
        )
    finally:
        raise HTTPException(status_code=201)


@app.delete("/metingen/{locatie}")
def delete_metingen(locatie: str, key: str = Depends(verify_api_key)):
    """Verwijder metingen en metinguren ouder dan 12 uur."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()
        locatieId = locatieId[0]
        cursor.execute(
            "SELECT COUNT(*) FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
            (locatieId,),
        )
        count = cursor.fetchone()[0]
        if count == 0:
            logging.warning(
                f"[API] 200 ACCEPTED: 404: Er zijn geen metingen ouder dan 12 uur voor {locatie}."
            )
            return {"detail": f"Er zijn geen metingen ouder dan 12 uur voor {locatie}."}

        cursor.execute(
            "SELECT metingenId FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
            (locatieId,),
        )
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute(
                "DELETE FROM metinguren WHERE metingenId = %s", (measurement_id,)
            )
        cursor.execute(
            "DELETE FROM metingen WHERE datetime < NOW() - INTERVAL 12 HOUR AND locatieId = %s",
            (locatieId,),
        )
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het delete-request van /metingen/{locatie}.",
            e,
        )
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()


########################################################################################################################
# VOORSPELLING / VOORSPELLINGEN ENDPOINTS
@app.get("/voorspellinguren/{locatie}")
# , response_model=List[VoorspellingUren]
def get_voorspellingen(locatie: str, db: Session = Depends(get_db)):
    """Haal alle metingen op uit de database en converteer ze naar een lijst van voorspellinguren objecten."""
    try:
        stmt = select(VoorspellingUren)
        voorspellingen = db.execute(stmt).all()
        for j in voorspellingen:
            for i in j:
                return i.zWaarde
        weervoorspelling = []
        for voorspelling in voorspellingen:
            weervoorspelling.append(VoorspellingUren(**voorspelling))
        return weervoorspelling
    except Exception as e:
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij get-request /voorspellinguren/{locatie}.",
            e,
        )

    #     datetime: str
    # temperature: float
    # zWaarde: int
    # beschrijving: Optional[str] = None
    # sneeuw: Optional[bool] = None


@app.post("/voorspellingen", response_model=Voorspelling)
def create_voorspelling(
    nieuwe_voorspelling: Voorspelling, key: str = Depends(verify_api_key)
):
    """Voeg een nieuwe voorspelling toe aan de database en retourneer een NieuweVoorspelling object."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO voorspellingen (locatieId, datetime) "
            f"VALUES ((SELECT locatieId FROM locaties WHERE locatie = %s), %s)",
            (nieuwe_voorspelling.locatie, nieuwe_voorspelling.datetime),
        )
        connection.commit()
        return {**nieuwe_voorspelling.dict()}
    except Exception as e:
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het post-request /voorspellingen, {nieuwe_voorspelling.locatie}, {nieuwe_voorspelling.datetime}",
            e,
        )
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.post("/voorspellinguren", response_model=List[VoorspellingUren])
def create_voorspelling_uren_batch(
    nieuwe_voorspellingen: List[VoorspellingUren], key: str = Depends(verify_api_key)
):
    """Voeg nieuwe voorspellingen toe aan de database en retourneer een lijst met NieuweVoorspellingUren objecten."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        voorspellingen_values = []
        for voorspelling in nieuwe_voorspellingen:
            voorspellingen_values.append(
                (voorspelling.datetime, voorspelling.temperature, voorspelling.zWaarde)
            )
        cursor.executemany(
            "INSERT INTO voorspellinguren (voorspellingenId, datetime, temperature, zWaarde) "
            f"VALUES ((SELECT voorspellingenId FROM voorspellingen ORDER BY voorspellingenId DESC LIMIT 1), %s, %s, %s)",
            voorspellingen_values,
        )
        connection.commit()
    except Exception as e:
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het post-request /voorspellinguren.",
            e,
        )
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/voorspellingen/{locatie}")
def delete_voorspellingen(locatie: str, key: str = Depends(verify_api_key)):
    """Verwijderen van voorspellingen en voorspellinguren behalve de meest recente."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT locatieId FROM locaties WHERE locatie = %s", (locatie,))
        locatieId = cursor.fetchone()[0]
        print(locatieId)
        cursor.execute(
            "SELECT COUNT(*) FROM voorspellingen WHERE locatieId = %s", (locatieId,)
        )
        count = cursor.fetchone()[0]
        if count == 0:
            logging.warning(
                f"[API] 200 ACCEPTED: 404: Er zijn geen voorspellingen voor {locatie}."
            )
            return {"detail": f"Er zijn geen voorspellingen voor {locatie}."}
        cursor.execute(
            "SELECT voorspellingenId FROM voorspellingen WHERE locatieId = %s ORDER BY datetime DESC LIMIT 1",
            (locatieId,),
        )
        latest_prediction_id = cursor.fetchone()[0]
        cursor.execute(
            "SELECT voorspellingenId FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s",
            (latest_prediction_id, locatieId),
        )
        old_measurement_ids = cursor.fetchall()
        for measurement_id_tuple in old_measurement_ids:
            measurement_id = measurement_id_tuple[0]
            cursor.execute(
                "DELETE FROM voorspellinguren WHERE voorspellingenId = %s",
                (measurement_id,),
            )
        cursor.execute(
            "DELETE FROM voorspellingen WHERE voorspellingenId != %s AND locatieId = %s",
            (latest_prediction_id, locatieId),
        )
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het delete-request /voorspellingen/{locatie}.",
            e,
        )
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()


########################################################################################################################
# LOCATIES ENDPOINTS


@app.get("/locaties", response_model=List[Locatie])
def get_locaties():
    """Haal alle locaties op uit de database en converteer ze naar een lijst van Locatie objecten."""
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
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij get-request /locaties.", e
        )
    finally:
        connection.close()


@app.post("/locaties", response_model=Locatie)
def create_locatie(nieuwe_locatie: Locatie, key: str = Depends(verify_api_key)):
    """Voeg een nieuwe locatie toe aan de database en retourneer een Locatie object."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO locaties (locatie) " "VALUES (%s)", (nieuwe_locatie.locatie,)
        )
        connection.commit()
        return {**nieuwe_locatie.dict()}
    except Exception as e:
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het post-request /locaties, {nieuwe_locatie.locatie}.",
            e,
        )
    finally:
        if connection.is_connected():
            connection.close()
            raise HTTPException(status_code=201)


@app.delete("/locaties/{locatie}")
def delete_locatie(locatie: str, key: str = Depends(verify_api_key)):
    """Verwijder een locatie uit de database."""
    connection = DB.connect_to_database()
    try:
        cursor = connection.cursor()
        connection.start_transaction()
        cursor.execute("SELECT COUNT(*) FROM locaties WHERE locatie = %s", (locatie,))
        locatie_count = cursor.fetchone()[0]
        if locatie_count > 0:
            cursor.execute(
                "DELETE FROM metinguren WHERE metingenId IN (SELECT metingenId FROM metingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s))",
                (locatie,),
            )
            cursor.execute(
                "DELETE FROM metingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s)",
                (locatie,),
            )
            cursor.execute(
                "DELETE FROM voorspellinguren WHERE voorspellingenId IN (SELECT voorspellingenId FROM voorspellingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s))",
                (locatie,),
            )
            cursor.execute(
                "DELETE FROM voorspellingen WHERE locatieId = (SELECT locatieId FROM locaties WHERE locatie = %s)",
                (locatie,),
            )
            cursor.execute("DELETE FROM locaties WHERE locatie = %s", (locatie,))
            connection.commit()
            return {"detail": f"Locatie {locatie} is verwijderd."}
        else:
            logging.warning(f"[API] 200 ACCEPTED: 404: Locatie {locatie} bestaat niet.")
            return {"detail": f"Locatie {locatie} bestaat niet."}
    except Exception as e:
        connection.rollback()
        connection.close()
        logging.error(
            f"[API] %s: Er is een fout opgetreden bij het delete-request /locaties/{locatie}.",
            e,
        )
        raise HTTPException(status_code=500)
    finally:
        if connection.is_connected():
            connection.commit()
            connection.close()
