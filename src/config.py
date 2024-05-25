import logging
import os


class Config:
    DEBUG = False
    SECRET_KEY = 'secret!'
    SCHEDULER_API_ENABLED = True
    LOGGING_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    LOGGING_LOCATION = 'data/web.log'
    LOGGING_LEVEL = logging.INFO
    VERSION = '2.4.1'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../data/data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOCK_SERVER_OPTIONS = {'ping_interval': 10}
