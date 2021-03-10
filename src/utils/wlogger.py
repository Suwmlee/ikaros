
from .. import app

class wlogger():

    @staticmethod
    def info(msg):
        try:
            app.logger.info(msg)
        except Exception as err:
            print(err)
            pass
    
    @staticmethod
    def error(msg):
        try:
            app.logger.error(msg)
        except Exception as err:
            print(err)
            pass
