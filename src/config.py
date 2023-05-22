import logging
import os


class Config:
    DEBUG = False
    SECRET_KEY = 'secret!'
    SCHEDULER_API_ENABLED = True
    LOGGING_FORMAT = '[%(asctime)s] %(module)-15s %(levelname)s : %(message)s'
    LOGGING_LOCATION = 'data/web.log'
    LOGGING_LEVEL = logging.INFO
    VERSION = '2.0.4'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../data/data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
