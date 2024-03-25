from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    DECIMAL,
    VARCHAR,
)
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from datetime import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends

load_dotenv()

DB_URL = (
    f"mysql+mysqlconnector://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWORD")}@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}?auth_plugin="
)
testing_DB_URL = "sqlite:///:memory:"

engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Metingen(Base):
    __tablename__ = "metingen"
    metingenId = Column(Integer, primary_key=True, autoincrement=True)
    locatieId = Column(Integer, ForeignKey("locaties.locatieId"))
    datetime = Column(DateTime)


class MetingUren(Base):
    __tablename__ = "metinguren"
    metingUrenId = Column(Integer, primary_key=True, autoincrement=True)
    metingenId = Column(Integer, ForeignKey("metingen.metingenId"))
    datetime = Column(DateTime)
    temperature = Column(DECIMAL(5, 2))
    pressure = Column(DECIMAL(5, 2))
    winddirection = Column(VARCHAR(255))


class Locaties(Base):
    __tablename__ = "locaties"
    locatieId = Column(Integer, primary_key=True, autoincrement=True)
    locatie = Column(VARCHAR(255))


class Voorspellingen(Base):
    __tablename__ = "voorspellingen"
    voorspellingId = Column(Integer, primary_key=True, autoincrement=True)
    locatieId = Column(Integer, ForeignKey("locaties.locatieId"))
    datetime = Column(DateTime)
    currenttemp = Column(DECIMAL(5, 2))
    zWaarde = Column(Integer)


class VoorspellingUren(Base):
    __tablename__ = "voorspellinguren"
    voorspellingUrenId = Column(Integer, primary_key=True, autoincrement=True)
    voorspellingId = Column(Integer, ForeignKey("voorspellingen.voorspellingId"))
    datetime = Column(DateTime)
    temperature = Column(DECIMAL(5, 2))
    zWaarde = Column(Integer)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

SessionLocal().add(eerste_meting)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.post("/items")
# def create_item(item: ItemCreate, db: session = Depends(get_db)) -> Item:
#     db_item = DBItem(**item.model_dump())
#     db.add(db_item)
#     return Item(**db_item.__dict__)
