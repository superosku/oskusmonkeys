#import os
#import sqlite3
from flask import Flask
from sqlalchemy import create_engine

def create_app(db_uri):
	app = Flask(__name__)
	#monkeyapp.database.init_engine("sqlite:///tmp/test.db")
	app.engine = create_engine(db_uri, convert_unicode=True)
	from monkeyapp.views import api
	app.register_blueprint(api)
	app.secret_key = "devays key"
	return app

#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    db_session.remove()


