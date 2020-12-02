import logging
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    SECRET_KEY = 'secret!'
    SCHEDULER_API_ENABLED = True
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(message)s'
    LOGGING_LOCATION = 'error.log'
    LOGGING_LEVEL = logging.ERROR
    VERSION = '0.0.1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'scraper.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
