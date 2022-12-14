# -*- coding: utf-8 -*-

import os
import json
import logging
import time
import subprocess
from flask import request, Response, current_app

from . import web
from ..service.configservice import localConfService
from ..bizlogic.schedulertask import cleanRecordsTask
from ..utils.regex import regexMatch


@web.route("/api/options/loglevel", methods=['GET', 'PUT'])
def loglevel():
    """
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
    """
    if request.method == 'GET':
        level = current_app.logger.level
        ret = {'loglevel': level}
        return json.dumps(ret)
    if request.method == 'PUT':
        content = request.get_json()
        if content and 'loglevel' in content:
            level = int(content.get('loglevel'))
            localConfService.updateLoglvl(level)
            current_app.logger.setLevel(level)
        else:
            localConfService.updateLoglvl(logging.INFO)
            current_app.logger.setLevel(logging.INFO)
        return Response(status=200)


@web.route("/api/options/cleanrecord", methods=['GET'])
def cleanErrData():
    """ clean record file not exist
    """
    cleanRecordsTask(True)
    return Response(status=200)

# TODO refactor log


def flask_logger():
    """creates logging information"""
    localPath = os.path.dirname(os.path.abspath(__file__))
    # TODO get web.log
    logfile = os.path.join(localPath, "..", "..", "data", "web.log")
    with open(logfile, encoding='UTF-8') as log_info:
        for i in range(25):
            data = log_info.read()
            yield data.encode()
            time.sleep(1)


@web.route("/api/options/logstream", methods=["GET"])
def stream():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream; charset=utf-8")


@web.route("/api/options/config", methods=["GET"])
def getLocalConfig():
    """returns config"""
    content = localConfService.getConfig().serialize()
    return json.dumps(content)


@web.route("/api/options/config", methods=['PUT'])
def updateLocalConf():
    content = request.get_json()
    localConfService.updateConfig(content)
    return Response(status=200)


@web.route("/api/options/check/lib", methods=['GET'])
def checklibversion():
    """ 检测scrapinglib版本
    """
    info = subprocess.run("python -m pip index -vv versions scrapinglib", shell=True, stdout=subprocess.PIPE, encoding="utf8")
    out = info.stdout
    current_app.logger.debug(out)
    install_matches = regexMatch(out, "INSTALLED:\ ([\d.]+)")
    latest_matches = regexMatch(out, "LATEST:[\ ]+([\d.]+)")
    installed = install_matches[0] if len(install_matches) == 1 else "Unknown"
    latest = latest_matches[0] if len(latest_matches) == 1 else "Unknown"
    ret = {
        "name": "scrapinglib",
        "installed": installed,
        "latest": latest
    }
    return json.dumps(ret)


@web.route("/api/options/check/lib", methods=['PUT'])
def updatelibversion():
    """ 更新scrapinglib
    """
    info = subprocess.run("python -m pip install scrapinglib -U", shell=True, stdout=subprocess.PIPE, encoding="utf8")
    current_app.logger.debug(info.stdout)
    return Response(status=200)
