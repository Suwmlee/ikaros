
import json
import os
from time import sleep
import datetime
from flask import render_template, request, Response, current_app

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..bizlogic.setting import settingService

# 记录日志读取位置
start_point = 0
basedir = os.path.abspath(os.path.dirname(__file__))


@web.route("/api/start", methods=['POST'])
def start_scraper():
    try:
        manager.start()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as err:
        current_app.logger.error(err)
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@web.route("/api/transfer", methods=['POST'])
def start_transfer():
    try:
        content = request.get_json()
        transfer.transfer(content['source_folder'], content['output_folder'], content['soft_prefix'], '')
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as err:
        current_app.logger.error(err)
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}



@web.route("/log/<int:lastnum>", methods=["GET"])
def stream(lastnum):
    loginfo = read_logs()
    """returns logging information"""
    return json.dumps({'lastnum': lastnum + 1, 'content': loginfo})


def read_logs():
    """ 读取web.log日志内容
    """
    fo = open(basedir + "/../../web.log", "rb")
    global start_point
    fo.seek(start_point, 1)
    logs = ""
    for line in fo.readlines():
        logs = logs + str(line.decode())
    start_point = fo.tell()
    fo.close()
    return logs
