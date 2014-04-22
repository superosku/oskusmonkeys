from sqlalchemy.orm import scoped_session, create_session
from sqlalchemy.ext.declarative import declarative_base

from flask import current_app

db_session = scoped_session(lambda: create_session(
    autocommit=False,
    autoflush=False,
    bind=current_app.engine))
Base = declarative_base()
Base.query = db_session.query_property()


def create_all():
    init_db()
    pass


def drop_all():
    Base.metadata.drop_all(bind=current_app.engine)


def init_db():
    Base.metadata.create_all(bind=current_app.engine)
