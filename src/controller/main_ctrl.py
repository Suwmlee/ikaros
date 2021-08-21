# -*- coding: utf-8 -*-

import json
import logging
import os
from flask import request, Response, current_app
import requests

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..bizlogic import rename
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import scrapingConfService, transConfigService
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
            f.close()
        return content
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/version", methods=['GET'])
def version():
    try:
        num = current_app.config['VERSION']
        return num
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/loglevel", methods=['PUT'])
def setloglevel():
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
        content = request.get_json()
        if content and 'level' in content:
            level = int(content.get('level'))
            current_app.logger.setLevel(level)
        else:
            current_app.logger.setLevel(logging.INFO)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


# action


@web.route("/api/client", methods=['GET'])
def scraping_single():
    """ for client
    """
    try:
        client_path = request.args.get('path')
        # TODO
        # 1. convert path to real path for flask
        # tr    /volume1/Media/Movies
        # flask /media/Movies
        real_path = str(client_path).replace("/volume1/Media","/media")
        if not os.path.exists(real_path):
            return Response(status=404)
        # 2. select scrape or transfer
        scrapingFolder = ['ACG/Collection','JAV']
        transferFolder = ['Movies','Documentry']
        flag_scraping = False
        flag_transfer = False
        for sc in scrapingFolder:
            if sc in real_path:
                flag_scraping = True
                break
        for sc in transferFolder:
            if sc in real_path:
                flag_transfer = True
                break
        # 3. run
        if flag_scraping:
            if os.path.isdir(real_path):
                manager.start_all(real_path)
            else:
                manager.start_single(real_path)
        # TODO run transfer, which one?
        # TODO emby API scan libraray
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scraping", methods=['POST'])
def start_scraping():
    try:
        content = request.get_json()
        if content and 'srcpath' in content:
            manager.start_single(content['srcpath'])
        else:
            manager.start_all()
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/transfer", methods=['POST'])
def start_transfer():
    try:
        content = request.get_json()
        transfer.transfer(content['source_folder'], content['output_folder'], content['linktype'],
                          content['soft_prefix'], content['escape_folder'], content['renameflag'], content['renameprefix'])
        
        if content.get('refresh_url'):
            refresh_url = content.get('refresh_url')
            requests.post(refresh_url)

        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/stopall", methods=['GET'])
def stop_all():
    try:
        taskService.updateTaskStatus(0, 'transfer')
        taskService.updateTaskStatus(0, 'scrape')
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/previewrename", methods=['POST'])
def previewrename():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['reg2'], content['prefix'], True)
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/renamebyreg", methods=['POST'])
def renamebyreg():
    try:
        content = request.get_json()
        ret = rename.renamebyreg(
            content['source_folder'], content['reg'], content['reg2'], content['prefix'], False)
        return json.dumps(ret)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/renamebyrep", methods=['POST'])
def renamebyreplace():
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
def editScrapingdata():
    try:
        content = request.get_json()
        scrapingrecordService.editRecord(
            content['id'], content['status'], content['scrapingname'], content['cnsubtag'], content['cdnum'])
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scrapingrecord/<sid>", methods=['DELETE'])
def deletescrapingrecord(sid):
    try:
        scrapingrecordService.deleteByID(sid)
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)


@web.route("/api/scrapingrecord", methods=['GET'])
def getscrapingrecord():
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
def gettransrecord():
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
def deltransrecord():
    """ 清理转移
    """
    try:
        transrecordService.deleteRecords()
        return Response(status=200)
    except Exception as err:
        log.error(err)
        return Response(status=500)
