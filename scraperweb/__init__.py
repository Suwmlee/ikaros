# -*- coding: utf-8 -*-
"""
    init app
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    """ create application
    """
    app = Flask(__name__, static_url_path='')
    app.config.from_object(Config)
    # Configure logging
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    db.app = app
    db.init_app(app)
    from .controller import register
    register(app)
    from .model import load_models
    load_models()
    db.create_all()

    return app
