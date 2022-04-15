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
    try:
        content = request.get_json()
        if content.get('path'):
            client_path = content.get('path')
            automation.start(client_path)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/auto/conf", methods=['GET'])
def getAutoConf():
    try:
        content = autoConfigService.getConfig().serialize()
        return json.dumps(content)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/auto/conf", methods=['PUT'])
def updateAutoConf():
    try:
        content = request.get_json()
        autoConfigService.updateConfig(content)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/auto/task", methods=['GET'])
def getAll():
    try:
        tasks = autoTaskService.getTasks()
        all = []
        for conf in tasks:
            all.append(conf.serialize())
        return json.dumps(all)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/auto/task", methods=['DELETE'])
def clientCleanTaskQueue():
    """ clean client task
    """
    try:
        automation.clean()
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
