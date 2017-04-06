#!venv/bin/python

import boto3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

import redis

from tempo import settings

# Configure app and other utilities
app = Flask(__name__)
app.config.from_object(settings)
auth = HTTPBasicAuth()

db = SQLAlchemy(app)

from tempo import models
db.create_all()
db.session.commit()

pool = redis.ConnectionPool(
    host = 'localhost',
    port = 6379,
    db = 0
)
r = redis.Redis(connection_pool = pool)

s3 = boto3.client('s3')
bucket = boto3.resource('s3').Bucket('tempo-songs')

from tempo import routes
