# -*- coding: utf-8 -*-
from .. import app


class log():
    """ use flask logger - standard Python logging
    """

    @staticmethod
    def info(msg):
        try:
            if app:
                app.logger.info(msg)
            else:
                print(msg)
        except Exception as err:
            print(err)
            pass

    @staticmethod
    def warning(msg):
        try:
            if app:
                app.logger.warning(msg)
            else:
                print(msg)
        except Exception as err:
            print(err)
            pass

    @staticmethod
    def error(msg):
        try:
            if app:
                app.logger.error(msg)
            else:
                print(msg)
        except Exception as err:
            print(err)
            pass

    @staticmethod
    def debug(msg):
        try:
            if app:
                app.logger.debug(msg)
            else:
                print(msg)
        except Exception as err:
            print(err)
            pass
