#!venv/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

from tempo import settings

# Configure app and other utilities
app = Flask(__name__)
app.config.from_object(settings)
auth = HTTPBasicAuth()

db = SQLAlchemy(app)

from tempo import models
db.create_all()
db.session.commit()

from tempo import routes
