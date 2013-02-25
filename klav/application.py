# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import *
from .database import init_db


def create_app(config):
    app = Flask(__name__)
    if config:
        app.config.from_object(config)

    app.db = SQLAlchemy(app)
    init_db(app)

    return app
