from sqlalchemy import create_engine

from app.db.models import Base


def add_all_tables(url):
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)


def add_table(url, model):
    engine = create_engine(url)
    model.__table__.create(engine)
