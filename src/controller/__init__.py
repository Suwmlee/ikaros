
import traceback
from flask import Blueprint, json, jsonify


web = Blueprint('web', __name__)


def init(app):
    from . import main_ctrl
    from . import viewsctrl
    from . import optionctrl
    from . import filescan_ctrl
    from . import scrapingctrl
    from . import transferctrl
    from . import automationctrl

    app.register_blueprint(web)

    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def handle_httpexception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        ret = {
            "code": 500,
            "name": "Internal Server Error",
            "description": "Internal Server Error, Please check the logs for details",
        }
        strs = traceback.format_exc()
        app.logger.error(strs)
        return jsonify(ret), 500
