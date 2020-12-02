
from flask import Blueprint


web = Blueprint('web', __name__ )


def register(app):
    from . import main_ctrl
    from . import setting_ctrl
    from . import view_ctrl

    app.register_blueprint(web)
