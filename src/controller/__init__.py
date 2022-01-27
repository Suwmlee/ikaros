
from flask import Blueprint


web = Blueprint('web', __name__ )


def register(app):
    from . import main_ctrl
    from . import view_ctrl
    from . import optionctrl
    from . import filescan_ctrl
    from . import scrapingctrl
    from . import transferctrl
    from . import automationctrl

    app.register_blueprint(web)
