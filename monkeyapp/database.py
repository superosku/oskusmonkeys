from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, create_session
from sqlalchemy.ext.declarative import declarative_base

from flask import current_app

#engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
#db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
db_session = scoped_session(lambda: create_session(autocommit=False, autoflush=False, bind=current_app.engine))
#db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=current_app.engine))

Base = declarative_base()
Base.query = db_session.query_property()
def create_all():
	init_db()
	pass
def drop_all():
	import monkeyapp.models
	Base.metadata.drop_all(bind=current_app.engine)
def init_db():
	import monkeyapp.models
	Base.metadata.create_all(bind=current_app.engine)

