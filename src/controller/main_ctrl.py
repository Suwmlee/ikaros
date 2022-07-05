# -*- coding: utf-8 -*-

import json
import os
from flask import request, Response, current_app

from . import web
from ..bizlogic import rename
from ..service.taskservice import taskService
from flask import current_app


@web.route("/api/intro", methods=['GET'])
def intro():
    localPath = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(localPath, "..", "..", "docs", 'intro.md'), encoding='utf-8') as f:
        content = f.read()
    return content


@web.route("/api/version", methods=['GET'])
def version():
    core_num = current_app.config['VERSION']
    version_info = "core_" + core_num
    localPath = os.path.dirname(os.path.abspath(__file__))
    webpath = os.path.join(localPath, "..", "..", "web", "static", 'version.txt')
    if os.path.exists(webpath):
        with open(webpath, encoding='utf-8') as f:
            web_sha = f.read()
            version_info = "web_" + web_sha[:7] + "  " + version_info
    return version_info

# action


@web.route("/api/stopall", methods=['GET'])
def resetAllTaskStatus():
    taskService.updateTaskStatus(taskService.getTask('transfer'), 0)
    taskService.updateTaskStatus(taskService.getTask('scrape'), 0)
    return Response(status=200)


@web.route("/api/previewrename", methods=['POST'])
def previewRename():
    content = request.get_json()
    ret = rename.renamebyreg(content['source_folder'], content['reg'], content['prefix'], True)
    return json.dumps(ret)


@web.route("/api/renamebyreg", methods=['POST'])
def renamebyRegex():
    content = request.get_json()
    ret = rename.renamebyreg(content['source_folder'], content['reg'], content['prefix'], False)
    return json.dumps(ret)


@web.route("/api/renamebyrep", methods=['POST'])
def renamebyReplace():
    content = request.get_json()
    ret = rename.rename(content['source_folder'], content['base'], content['newfix'])
    return json.dumps(ret)
