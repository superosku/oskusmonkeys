from flask import Flask
from sqlalchemy import create_engine


def create_app(db_uri):
    app = Flask(__name__)
    app.engine = create_engine(db_uri, convert_unicode=True)
    from monkeyapp.views import api
    app.register_blueprint(api)
    app.secret_key = "devays key"
    return app
