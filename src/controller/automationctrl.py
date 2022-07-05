# -*- coding: utf-8 -*-
'''
'''
import json

from flask import request, Response
from flask import current_app
from . import web
from ..bizlogic import automation
from ..service.configservice import autoConfigService
from ..service.taskservice import autoTaskService


@web.route("/api/client", methods=['POST'])
def clientAutoTask():
    """ for client
    """
    content = request.get_json()
    if content.get('path'):
        client_path = content.get('path')
        automation.start(client_path)
    return Response(status=200)


@web.route("/api/auto/conf", methods=['GET'])
def getAutoConf():
    content = autoConfigService.getConfig().serialize()
    return json.dumps(content)


@web.route("/api/auto/conf", methods=['PUT'])
def updateAutoConf():
    content = request.get_json()
    autoConfigService.updateConfig(content)
    return Response(status=200)


@web.route("/api/auto/task", methods=['GET'])
def getAll():
    tasks = autoTaskService.getTasks()
    all = []
    for conf in tasks:
        all.append(conf.serialize())
    return json.dumps(all)


@web.route("/api/auto/task", methods=['DELETE'])
def clientCleanTaskQueue():
    """ clean client task
    """
    automation.clean()
    return Response(status=200)
