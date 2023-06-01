
from flask_sock import Sock


wsocket = Sock()


def init(app):
    from . import wsloger

    wsocket.init_app(app)
