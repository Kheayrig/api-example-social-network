def add_all_tables():
    base.Base.metadata.create_all(bind=base.engine)


def add_table(model):
    model.__table__.create(base.engine)
