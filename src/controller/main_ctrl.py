# -*- coding: utf-8 -*-

import json
import os
from flask import request, Response, current_app

from . import web
from ..bizlogic import rename
from ..service.taskservice import taskService
from flask import current_app
# from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
# executor = ThreadPoolExecutor(2)

# Intro


@web.route("/api/intro", methods=['GET'])
def intro():
    try:
        localPath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(localPath, "..", "..", "docs", 'intro.md'), encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/version", methods=['GET'])
def version():
    try:
        core_num = current_app.config['VERSION']
        version_info = "core_" + core_num
        localPath = os.path.dirname(os.path.abspath(__file__))
        webpath = os.path.join(localPath, "..", "..",
                               "web", "static", 'version.txt')
        if os.path.exists(webpath):
            with open(webpath, encoding='utf-8') as f:
                web_sha = f.read()
                version_info = "web_" + web_sha[:7] + "  " + version_info
        return version_info
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


# action


@web.route("/api/stopall", methods=['GET'])
def resetAllTaskStatus():
    try:
        taskService.updateTaskStatus(taskService.getTask('transfer'), 0)
        taskService.updateTaskStatus(taskService.getTask('scrape'), 0)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/previewrename", methods=['POST'])
def previewRename():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['prefix'], True)
        return json.dumps(ret)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/renamebyreg", methods=['POST'])
def renamebyRegex():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['prefix'], False)
        return json.dumps(ret)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/renamebyrep", methods=['POST'])
def renamebyReplace():
    try:
        content = request.get_json()
        ret = rename.rename(content['source_folder'],
                            content['base'], content['newfix'])
        return json.dumps(ret)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
