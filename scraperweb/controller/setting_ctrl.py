
import json
import os
from time import sleep
import datetime
from flask import render_template, request, Response

from . import web
from ..bizlogic.setting import settingService
from ..utils.wlogger import wlogger


@web.route("/api/setting", methods=['GET'])
def getSetting():
    try:
        content = settingService.getSetting().serialize()
        return json.dumps(content)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/setting", methods=['POST'])
def updateSetting():
    try:
        content = request.get_json()
        settingService.updateSetting(content)
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)
