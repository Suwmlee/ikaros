# -*- coding: utf-8 -*-
"""
    init app
"""
import logging
import flask_migrate
from flask import Flask
from logging.handlers import TimedRotatingFileHandler
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = flask_migrate.Migrate()
app = None


def create_app():
    """ create application
    """
    global app
    app = Flask(__name__, static_url_path='', static_folder='../web/static/', template_folder='../web/templates/')
    app.config.from_object(Config)
    # Configure logging
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler = TimedRotatingFileHandler(app.config['LOGGING_LOCATION'], encoding="utf-8", when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])

    db.app = app
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from . import controller
    from . import model
    controller.register(app)
    model.load_models()
    db.create_all()
    with app.app_context():
        try:
            app.logger.info("Initialization: upgrade db")
            flask_migrate.upgrade()
        except Exception as e:
            app.logger.info(e)
            app.logger.info("Initialization: fix alembic version")
            flask_migrate.stamp()

    from .service.schedulerservice import schedulerService
    schedulerService.init(app)
    schedulerService.start()
    schedulerService.addJob('initJob', resetDefaults, args=[schedulerService.scheduler], seconds=3)

    return app


def resetDefaults(scheduler):
    scheduler.remove_job(id='initJob')
    from .service.taskservice import autoTaskService
    from .service.configservice import localConfService
    from .bizlogic.automation import checkTaskQueue
    from .bizlogic.schedulertask import initScheduler
    scheduler.app.logger.info("Initialization: start")
    conf = localConfService.getConfig()
    if conf.loglevel:
        scheduler.app.logger.setLevel(conf.loglevel)
        scheduler.app.logger.info(f"Initialization: set loglevel {conf.loglevel}")
    autoTaskService.reset()
    with scheduler.app.app_context():
        checkTaskQueue()
    initScheduler()
    scheduler.app.logger.info("Initialization: finished")
