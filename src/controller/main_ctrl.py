# -*- coding: utf-8 -*-

import json
import logging
import os
from flask import request, Response, current_app

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..bizlogic import rename
from ..bizlogic import automation
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import scrapingConfService, transConfigService, autoConfigService
from ..service.taskservice import taskService
from ..utils.log import log
# from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
# executor = ThreadPoolExecutor(2)

# Intro
@web.route("/api/intro", methods=['GET'])
def intro():
    try:
        localPath = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(localPath,"..","..", 'README.md'), encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/version", methods=['GET'])
def version():
    try:
        core_num = current_app.config['VERSION']
        version_info = "core_" + core_num
        localPath = os.path.dirname(os.path.abspath(__file__))
        webpath = os.path.join(localPath,"..","..", "web", "static", 'version.txt')
        if os.path.exists(webpath):
            with open(webpath, encoding='utf-8') as f:
                web_sha = f.read()
                version_info = "web_" + web_sha[:7] + "  " + version_info
        return version_info
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/loglevel", methods=['GET', 'PUT'])
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
    try:
        if request.method == 'GET':
            level = current_app.logger.level
            ret = {'loglevel': level}
            return json.dumps(ret)
        if request.method == 'PUT':
            content = request.get_json()
            if content and 'loglevel' in content:
                level = int(content.get('loglevel'))
                current_app.logger.setLevel(level)
            else:
                current_app.logger.setLevel(logging.INFO)
            return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


# action


@web.route("/api/client", methods=['POST'])
def clientAutoTask():
    """ for client

#!/bin/bash
TR_DOWNLOADS="$TR_TORRENT_DIR/$TR_TORRENT_NAME"
curl -XPOST http://127.0.0.1:12346/api/client -H 'Content-Type: application/json' \
--data @<(cat <<EOF
{"path":"$TR_DOWNLOADS"}
EOF
)
    """
    try:
        content = request.get_json()
        if content.get('path'):
            client_path = content.get('path')
            automation.start(client_path)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/client/clean", methods=['GET'])
def clientCleanTaskQueue():
    """ clean client task
    """
    try:
        automation.clean()
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scraping", methods=['POST'])
def startScraping():
    try:
        content = request.get_json()
        if content and content.get('srcpath'):
            filepath = content.get('srcpath')
            if os.path.exists(filepath) and os.path.isfile(filepath):
                manager.startScrapingSingle(filepath)
        else:
            manager.startScrapingAll()
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transfer", methods=['POST'])
def startTransfer():
    try:
        content = request.get_json()
        transfer.ctrlTransfer(content['source_folder'], content['output_folder'], 
                               content['linktype'], content['soft_prefix'], 
                               content['escape_folder'],
                               content['renameflag'],
                               content['clean_others'], content['replace_CJK'],
                               content.get('refresh_url'))
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/stopall", methods=['GET'])
def resetAllTaskStatus():
    try:
        taskService.updateTaskStatus(0, 'transfer')
        taskService.updateTaskStatus(0, 'scrape')
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/previewrename", methods=['POST'])
def previewRename():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['prefix'], True)
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/renamebyreg", methods=['POST'])
def renamebyRegex():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['prefix'], False)
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/renamebyrep", methods=['POST'])
def renamebyReplace():
    try:
        content = request.get_json()
        ret = rename.rename(content['source_folder'], content['base'], content['newfix'])
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)

# scrapingconf


@web.route("/api/scrapingconf", methods=['GET'])
def getScrapingConf():
    try:
        content = scrapingConfService.getSetting().serialize()
        return json.dumps(content)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scrapingconf", methods=['POST'])
def updateScapingConf():
    try:
        content = request.get_json()
        scrapingConfService.updateSetting(content)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)

# scrapingrecords


@web.route("/api/scrapingrecord", methods=['PUT'])
def editScrapingData():
    try:
        content = request.get_json()
        scrapingrecordService.editRecord(
            content['id'], content['status'], content['scrapingname'], content['cnsubtag'], content['cdnum'])
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scrapingrecord/<sid>", methods=['DELETE'])
def deleteScrapingRecord(sid):
    try:
        scrapingrecordService.deleteByID(sid)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scrapingrecord", methods=['GET'])
def getScrapingRecord():
    """ 查询
    """
    try:
        page = int(request.args.get('page'))
        size = int(request.args.get('size'))
        # 排序  cnsubtag|status|updatetime,descending|ascending
        sortprop = request.args.get('sortprop')
        sortorder = request.args.get('sortorder')
        # 模糊查询
        blur = request.args.get('blur')
        if not blur:
            blur = ''
        if not sortprop:
            sortprop = ''
            sortorder = 'desc'

        infos = scrapingrecordService.queryByPage(
            page, size, sortprop, sortorder, blur)
        data = []
        for i in infos.items:
            data.append(i.serialize())
        ret = dict()
        ret['data'] = data
        ret['total'] = infos.total
        ret['pages'] = infos.pages
        ret['page'] = page
        taskinfo = taskService.getTask('scrape')
        if taskinfo.status == 2:
            ret['running'] = True
            ret['tasktotal'] = taskinfo.total
            ret['taskfinished'] = taskinfo.finished
        else:
            ret['running'] = False
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)

# transconf


@web.route("/api/transconf/all", methods=['GET'])
def getTransConfs():
    """ 查询转移配置
    """
    try:
        configs = transConfigService.getConfiglist()
        all = []
        for conf in configs:
            all.append(conf.serialize())
        return json.dumps(all)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transconf", methods=['POST'])
def addTransConf():
    """ 新增转移配置
    """
    try:
        content = request.get_json()
        content['id'] = None
        config = transConfigService.updateConf(content)
        return json.dumps(config.serialize())
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transconf", methods=['PUT'])
def updateTransConf():
    """ 更新转移配置
    """
    try:
        content = request.get_json()
        config = transConfigService.updateConf(content)
        return json.dumps(config.serialize())
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transconf/<cid>", methods=['DELETE'])
def deleteTransConf(cid):
    """ 删除转移配置
    """
    try:
        iid = int(cid)
        transConfigService.deleteConf(iid)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)

# transrecord


@web.route("/api/transrecord", methods=['GET'])
def getTransRecord():
    """ 查询
    """
    try:
        page = request.args.get('page')
        pagenum = int(page)
        size = int(request.args.get('size'))
        sort = 0
        infos = transrecordService.queryByPage(pagenum, size, sort)
        data = []
        for i in infos.items:
            data.append(i.serialize())
        ret = dict()
        ret['data'] = data
        ret['total'] = infos.total
        ret['pages'] = infos.pages
        ret['page'] = pagenum
        taskinfo = taskService.getTask('transfer')
        if taskinfo.status == 2:
            ret['running'] = True
            ret['tasktotal'] = taskinfo.total
            ret['taskfinished'] = taskinfo.finished
        else:
            ret['running'] = False
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transrecord", methods=['DELETE'])
def delTransRecord():
    """ 清理转移
    """
    try:
        transrecordService.deleteRecords()
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)

# autoconf


@web.route("/api/autoconf", methods=['GET'])
def getAutoConf():
    try:
        content = autoConfigService.getSetting().serialize()
        return json.dumps(content)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/autoconf", methods=['POST'])
def updateAutoConf():
    try:
        content = request.get_json()
        autoConfigService.updateSetting(content)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)
