import logging
import os


class Config:
    DEBUG = False
    SECRET_KEY = 'secret!'
    SCHEDULER_API_ENABLED = True
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(message)s'
    LOGGING_LOCATION = 'database/web.log'
    LOGGING_LEVEL = logging.INFO
    VERSION = '0.0.1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
