from app.db.base import engine
from app.db.models import Base


def add_all_tables():
    Base.metadata.create_all(bind=engine)


def add_table(model):
    model.__table__.create(engine)
