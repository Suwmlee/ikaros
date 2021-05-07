
from flask import Blueprint


web = Blueprint('web', __name__ )


def register(app):
    from . import main_ctrl
    from . import view_ctrl
    from . import backup_ctrl
    from . import filescan_ctrl

    app.register_blueprint(web)
