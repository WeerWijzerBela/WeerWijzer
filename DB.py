from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Numeric,
    BLOB,
    text,
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from logfiles.log import logging
from datetime import datetime, timedelta
import csv
import os
import random
import base64
from dotenv import load_dotenv
from runWeerWijzer import bereken_zambretti

load_dotenv()


# Database connection parameters
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

# Creating engine
engine = create_engine(f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
# engine = create_engine(f"sqlite:///tables.db")

# Creating a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Locatie(Base):
    __tablename__ = "locaties"

    locatieId = Column(Integer, primary_key=True, autoincrement=True)
    locatie = Column(String(255), nullable=False)

    metingen = relationship("Meting", back_populates="locatie")
    voorspellingen = relationship(
        "Voorspelling", back_populates="locatie"
    )  # Voeg deze relatie toe


class Meting(Base):
    __tablename__ = "metingen"

    metingenId = Column(Integer, primary_key=True, autoincrement=True)
    locatieId = Column(Integer, ForeignKey("locaties.locatieId"), nullable=False)
    datetime = Column(DateTime, default=datetime.now)

    locatie = relationship("Locatie", back_populates="metingen")
    metinguren = relationship("MetingUren", back_populates="meting")


class MetingUren(Base):
    __tablename__ = "metinguren"

    metingUrenId = Column(Integer, primary_key=True, autoincrement=True)
    metingenId = Column(Integer, ForeignKey("metingen.metingenId"), nullable=False)
    datetime = Column(DateTime)
    temperature = Column(Numeric(5, 2))
    pressure = Column(Numeric(6, 2))
    winddirection = Column(Numeric(5, 2))  ##AANGEPAST NAAR DECIMAL

    meting = relationship("Meting", back_populates="metinguren")


class Voorspelling(Base):
    __tablename__ = "voorspellingen"

    voorspellingenId = Column(Integer, primary_key=True, autoincrement=True)
    locatieId = Column(Integer, ForeignKey("locaties.locatieId"), nullable=False)
    datetime = Column(DateTime)

    locatie = relationship(
        "Locatie", back_populates="voorspellingen"
    )  # Voeg deze relatie toe
    voorspellinguren = relationship("VoorspellingUren", back_populates="voorspelling")


class VoorspellingUren(Base):
    __tablename__ = "voorspellinguren"

    voorspellingUrenId = Column(Integer, primary_key=True, autoincrement=True)
    voorspellingenId = Column(
        Integer, ForeignKey("voorspellingen.voorspellingenId"), nullable=False
    )
    zWaarde = Column(Integer, ForeignKey("zwaarden.zWaarde"), nullable=False)
    datetime = Column(DateTime)
    temperature = Column(Numeric(5, 2))

    voorspelling = relationship("Voorspelling", back_populates="voorspellinguren")
    zwaarde = relationship(
        "zWaarden", back_populates="voorspellinguren"
    )  # Voeg deze relatie toe


class zWaarden(Base):
    __tablename__ = "zwaarden"

    zWaarde = Column(Integer, primary_key=True)
    beschrijving = Column(String(100), nullable=True)

    voorspellinguren = relationship(
        "VoorspellingUren", back_populates="zwaarde"
    )  # Voeg deze relatie toe

class Image(Base):
    __tablename__ = "images"

    imageId = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(BLOB, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Create all tables in the database
    try:
        Base.metadata.create_all(bind=engine)
        seed_db()
    except Exception as e:
        logging.error(
            f"Er is een fout opgetreden bij het initialiseren van de database: {e}"
        )
        return e


def seed_db(TestingDB=False):
    try:
        if TestingDB is not False:
            db = TestingDB
        else:
            db = SessionLocal()
        if db.bind.url.drivername != "sqlite":
            db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        # Datum aanmaken voor de seed data, afgerond op dichtbijzijnste uur
        datumNu = datetime.now() - timedelta(hours=48)
        datumNu = datumNu.replace(
            second=0, microsecond=0, minute=0, hour=datumNu.hour
        ) + timedelta(hours=datumNu.minute // 30)

        if db.query(Locatie).count() == 0:
            locaties = [
                Locatie(locatieId=1, locatie="Apeldoorn"),
                Locatie(locatieId=2, locatie="Amersfoort"),
            ]
            db.add_all(locaties)
            db.commit()

        if db.query(Meting).count() == 0:
            metingen = [
                Meting(metingenId=1, locatieId=1, datetime=datumNu),
                Meting(metingenId=2, locatieId=2, datetime=datumNu),
                Meting(
                    metingenId=3,
                    locatieId=1,
                    datetime=datetime.now() - timedelta(hours=1),
                ),
                Meting(
                    metingenId=4,
                    locatieId=2,
                    datetime=datetime.now() - timedelta(hours=1),
                ),
                Meting(metingenId=5, locatieId=1, datetime=datetime.now()),
                Meting(metingenId=6, locatieId=2, datetime=datetime.now()),
            ]
            db.add_all(metingen)
            db.commit()

        if db.query(MetingUren).count() == 0:

            # Voegt per meting/locatie 48 metingUren toe
            for meting in db.query(Meting).all():
                metingUren = []
                for metinguur in range(1, 49):
                    metingUren.append(
                        MetingUren(
                            metingenId=meting.metingenId,
                            datetime=datumNu + timedelta(hours=metinguur),
                            temperature=random.randint(0, 20),
                            pressure=random.randint(980, 999),
                            winddirection=random.randint(0, 360),
                        )
                    )
                db.add_all(metingUren)
                db.commit()
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

        if db.query(Voorspelling).count() == 0:
            voorspellingen = [
                Voorspelling(voorspellingenId=1, locatieId=1, datetime=datumNu),
                Voorspelling(voorspellingenId=2, locatieId=2, datetime=datumNu),
                Voorspelling(
                    voorspellingenId=3,
                    locatieId=1,
                    datetime=datetime.now() - timedelta(hours=1),
                ),
                Voorspelling(
                    voorspellingenId=4,
                    locatieId=2,
                    datetime=datetime.now() - timedelta(hours=1),
                ),
                Voorspelling(voorspellingenId=5, locatieId=1, datetime=datetime.now()),
                Voorspelling(voorspellingenId=6, locatieId=2, datetime=datetime.now()),
            ]
            db.add_all(voorspellingen)
            db.commit()

        if db.query(VoorspellingUren).count() == 0:
            for voorspelling in db.query(Voorspelling).all():
                voorspellingUren = []
                recentste_meting = (
                    db.query(Meting)
                    .filter(Meting.locatieId == Locatie.locatieId)
                    .order_by(Meting.datetime.desc())
                    .first()
                )
                metinguren = (
                    db.query(MetingUren)
                    .filter(MetingUren.metingenId == recentste_meting.metingenId)
                    .all()
                )
                for i, meting in enumerate(metinguren):
                    if 0 < i < 5:
                        continue
                    voorspellingUren.append(
                        VoorspellingUren(
                            voorspellingenId=voorspelling.voorspellingenId,
                            zWaarde=bereken_zambretti(
                                float(meting.pressure),
                                (
                                    float(metinguren[1].pressure)
                                    if i == 0
                                    else float(metinguren[i - 3].pressure)
                                ),
                                meting.winddirection,
                            ),
                            datetime=meting.datetime,
                            temperature=meting.temperature,
                        )
                    )
                db.add_all(voorspellingUren)
                db.commit()
        if db.query(Image).count() != 0:
            image_directory = "templates/pictures"
            for image in os.listdir(image_directory):
                if image.endswith(".png"):
                    image_name = os.path.splitext(image)[0]
                    if image_name.isdigit():
                        with open(f"{image_directory}/{image}", "rb") as file:
                            image_data = file.read()
                            image_base64 = base64.b64encode(image_data).decode("utf-8")
                            db.add(Image(imageId=int(image_name), image=image_base64))
                            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Er is een fout opgetreden bij het seeden van de database: {e}")
        return e
    finally:
        db.commit()
        if db.bind.url.drivername != "sqlite":
            db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.close()
