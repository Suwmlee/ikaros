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
    """ Beta 检测scrapinglib版本
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
    """ Beta 更新scrapinglib
    """
    info = subprocess.run("python -m pip install scrapinglib -U", shell=True, stdout=subprocess.PIPE, encoding="utf8")
    current_app.logger.debug(info.stdout)
    return Response(status=200)
