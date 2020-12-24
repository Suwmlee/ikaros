# -*- coding: utf-8 -*-
"""
    init app
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()
app = None

def create_app():
    """ create application
    """
    global app
    app = Flask(__name__, static_url_path='')
    app.config.from_object(Config)
    # Configure logging
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'], encoding="utf-8")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])

    db.app = app
    db.init_app(app)
    from .controller import register
    register(app)
    from .model import load_models
    load_models()
    db.create_all()

    return app
