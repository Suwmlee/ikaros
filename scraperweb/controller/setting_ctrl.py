
import json
import os
from time import sleep
import datetime
from flask import render_template, request, Response, current_app

from . import web
from ..bizlogic.setting import settingService

@web.route("/api/setting", methods=['GET'])
def getSetting():
    try:
        content = settingService.getSetting().serialize()
        return json.dumps(content), 200, {'ContentType': 'application/json'}
    except Exception as err:
        current_app.logger.error(err)
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@web.route("/api/setting", methods=['POST'])
def updateSetting():
    try:
        content = request.get_json()
        settingService.updateSetting(content)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as err:
        current_app.logger.error(err)
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
