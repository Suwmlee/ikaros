import logging
import os, platform


class Config:
    DEBUG = False
    SECRET_KEY = 'secret!'
    SCHEDULER_API_ENABLED = True
    LOGGING_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    LOGGING_LOCATION = 'data/web.log'
    LOGGING_LEVEL = logging.INFO
    VERSION = '2.5.0'
    BASE_DATABASE_URI = '../data/data.db'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DATABASE_URI}" if platform.system() != "Darwin" else f"sqlite:///{os.path.abspath(BASE_DATABASE_URI.removeprefix('../'))}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOCK_SERVER_OPTIONS = {'ping_interval': 10}
