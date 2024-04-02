from DB import get_db, init_db, Base, engine

DATABASE_URL = "sqlite:///:memory:"


def test_get_db():
    assert isinstance(get_db(), object)


def test_init_db():
    Base.metadata.drop_all(bind=engine)
    assert init_db() is None
