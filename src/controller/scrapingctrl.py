# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app

from . import web
from ..bizlogic.manager import startScrapingAll, startScrapingSingle
from ..bizlogic.schedulertask import cleanTorrents
from ..service.configservice import localConfService, scrapingConfService
from ..service.recordservice import scrapingrecordService
from ..service.taskservice import taskService


@web.route("/api/scraping", methods=['POST'])
def startScraping():
    content = request.get_json()
    if content and content.get('id'):
        cid = content.get('id')
        startScrapingAll(cid)
    return Response(status=200)


@web.route("/api/scraping/single", methods=['POST'])
def startScrapingdirect():
    content = request.get_json()
    if content and content.get('srcpath'):
        filepath = content.get('srcpath')
        cid = content.get('configid')
        startScrapingSingle(cid, filepath, True)
    return Response(status=200)


@web.route("/api/scraping/conf/<sid>", methods=['GET'])
def getScrapingConf(sid):
    if sid == 'all':
        configs = scrapingConfService.getConfiglist()
        all = []
        for conf in configs:
            all.append(conf.serialize())
        return json.dumps(all)
    else:
        content = scrapingConfService.getConfig(sid).serialize()
        return json.dumps(content)


@web.route("/api/scraping/conf", methods=['POST'])
def addConf():
    """ 新增配置
    """
    content = request.get_json()
    content['id'] = None
    config = scrapingConfService.updateConfig(content)
    return json.dumps(config.serialize())


@web.route("/api/scraping/conf", methods=['PUT'])
def updateScapingConf():
    content = request.get_json()
    scrapingConfService.updateConfig(content)
    return Response(status=200)


@web.route("/api/scraping/conf/<cid>", methods=['DELETE'])
def deleteScrapingConf(cid):
    """ 删除配置
    """
    iid = int(cid)
    scrapingConfService.deleteConf(iid)
    return Response(status=200)


@web.route("/api/scraping/record", methods=['DELETE'])
def deleteScrapingRecordIds():
    content = request.get_json()
    delsrc = content.get('delsrc')
    ids = content.get('ids')
    delrecords = scrapingrecordService.deleteByIds(ids, delsrc)
    if delsrc:
        localconfig = localConfService.getConfig()
        cleanTorrents(delrecords, localconfig)
    return Response(status=200)


@web.route("/api/scraping/record", methods=['GET'])
def getScrapingRecord():
    """ 查询
    """
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
    taskinfo = taskService.getTask('scrape')
    if taskinfo.status == 2:
        ret['running'] = True
        ret['tasktotal'] = taskinfo.total
        ret['taskfinished'] = taskinfo.finished
    else:
        ret['running'] = False
    return json.dumps(ret)


@web.route("/api/scraping/record", methods=['PUT'])
def editScrapingData():
    content = request.get_json()
    scrapingrecordService.editRecord(content['id'],
                                     content['status'],
                                     content['scrapingname'],
                                     content['cnsubtag'],
                                     content['leaktag'],
                                     content['uncensoredtag'],
                                     content['hacktag'],
                                     content['cdnum'],
                                     content['deadtime'])
    return Response(status=200)
