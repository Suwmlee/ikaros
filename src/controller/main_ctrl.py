# -*- coding: utf-8 -*-

import json
import os
import datetime
from time import sleep
from threading import Lock
from flask import request, Response

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import scrapingConfService, transConfigService
from ..service.taskservice import taskService
from ..utils.wlogger import wlogger
# from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
# executor = ThreadPoolExecutor(2)

# action


@web.route("/api/scraping", methods=['POST'])
def start_scraping():
    try:
        # executor.submit(manager.start)
        manager.start()
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/transfer", methods=['POST'])
def start_transfer():
    try:
        content = request.get_json()
        transfer.transfer(content['source_folder'], content['output_folder'], content['linktype'], content['soft_prefix'], content['escape_folder'])
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/stopall", methods=['POST'])
def stop_all():
    try:
        taskService.updateTaskStatus(0, 'transfer')
        taskService.updateTaskStatus(0, 'scrape')
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)

# scrapingconf


@web.route("/api/scrapingconf", methods=['GET'])
def getScrapingConf():
    try:
        content = scrapingConfService.getSetting().serialize()
        return json.dumps(content)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/scrapingconf", methods=['POST'])
def updateScapingConf():
    try:
        content = request.get_json()
        scrapingConfService.updateSetting(content)
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)

# scrapingrecords


@web.route("/api/scrapingrecord", methods=['PUT'])
def editScrapingdata():
    try:
        content = request.get_json()
        scrapingrecordService.editRecord(content['id'], content['status'], content['scrapingname'], content['cnsubtag'])
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/scrapingrecord/<sid>", methods=['DELETE'])
def deletescrapingrecord(sid):
    try:
        scrapingrecordService.deleteByID(sid)
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
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

        infos = scrapingrecordService.queryByPage(page, size, sortprop, sortorder, blur)
        data = []
        for i in infos.items:
            data.append(i.serialize())
        ret = dict()
        ret['data'] = data
        ret['total'] = infos.total
        ret['pages'] = infos.pages
        ret['page'] = page
        if taskService.getTask('scrape').status == 2:
            ret['running'] = True
        else:
            ret['running'] = False
        return json.dumps(ret)
    except Exception as err:
        wlogger.info(err)
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
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/transconf", methods=['POST'])
def addTransConf():
    """ 新增转移配置
    """
    try:
        content = request.get_json()
        content['id'] = -1
        config = transConfigService.updateConf(content)
        return json.dumps(config.serialize())
    except Exception as err:
        wlogger.info(err)
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
        wlogger.info(err)
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
        wlogger.info(err)
        return Response(status=500)

# transrecord


@web.route("/api/transrecord/<page>", methods=['GET'])
def gettransrecord(page):
    try:
        pagenum = int(page)
        size = 10
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
        if taskService.getTask('transfer').status == 2:
            ret['running'] = True
        else:
            ret['running'] = False
        return json.dumps(ret)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)
