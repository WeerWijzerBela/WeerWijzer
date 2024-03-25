from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

# Creating engine
engine = create_engine(f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# Creating a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Locatie(Base):
    __tablename__ = "locaties"

    locatieId = Column(Integer, primary_key=True, autoincrement=True)
    locatie = Column(String(255), nullable=False)

    metingen = relationship("Meting", back_populates="locatie")
    voorspellingen = relationship("Voorspelling", back_populates="locatie")  # Voeg deze relatie toe


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
    pressure = Column(Numeric(5, 2))
    winddirection = Column(String(255))

    meting = relationship("Meting", back_populates="metinguren")


class Voorspelling(Base):
    __tablename__ = "voorspellingen"

    voorspellingenId = Column(Integer, primary_key=True, autoincrement=True)
    locatieId = Column(Integer, ForeignKey("locaties.locatieId"), nullable=False)
    datetime = Column(DateTime)

    locatie = relationship("Locatie", back_populates="voorspellingen")  # Voeg deze relatie toe
    voorspellinguren = relationship("VoorspellingUren", back_populates="voorspelling")


class VoorspellingUren(Base):
    __tablename__ = "voorspellinguren"

    voorspellingUrenId = Column(Integer, primary_key=True, autoincrement=True)
    voorspellingenId = Column(Integer, ForeignKey("voorspellingen.voorspellingenId"), nullable=False)
    zWaarde = Column(Integer, ForeignKey("zwaarden.zWaarde"), nullable=False)
    datetime = Column(DateTime)
    temperature = Column(Numeric(5, 2))

    voorspelling = relationship("Voorspelling", back_populates="voorspellinguren")
    zwaarde = relationship("zWaarden", back_populates="voorspellinguren")  # Voeg deze relatie toe


class zWaarden(Base):
    __tablename__ = "zwaarden"

    zWaarde = Column(Integer, primary_key=True)
    beschrijving = Column(String(100), nullable=True)

    voorspellinguren = relationship("VoorspellingUren", back_populates="zwaarde")  # Voeg deze relatie toe


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
