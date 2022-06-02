# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app
from . import web
from ..bizlogic.manager import startScrapingAll, startScrapingSingle
from ..service.configservice import scrapingConfService
from ..service.recordservice import scrapingrecordService
from ..service.taskservice import taskService


@web.route("/api/scraping", methods=['POST'])
def startScraping():
    try:
        content = request.get_json()
        if content and content.get('id'):
            cid = content.get('id')
            startScrapingAll(cid)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/single", methods=['POST'])
def startScrapingdirect():
    try:
        content = request.get_json()
        if content and content.get('srcpath'):
            filepath = content.get('srcpath')
            cid = content.get('configid')
            startScrapingSingle(cid, filepath)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/conf/<sid>", methods=['GET'])
def getScrapingConf(sid):
    try:
        if sid == 'all':
            configs = scrapingConfService.getConfiglist()
            all = []
            for conf in configs:
                all.append(conf.serialize())
            return json.dumps(all)
        else:
            content = scrapingConfService.getConfig(sid).serialize()
            return json.dumps(content)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/conf", methods=['POST'])
def addConf():
    """ 新增配置
    """
    try:
        content = request.get_json()
        content['id'] = None
        config = scrapingConfService.updateConfig(content)
        return json.dumps(config.serialize())
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/conf", methods=['PUT'])
def updateScapingConf():
    try:
        content = request.get_json()
        scrapingConfService.updateConfig(content)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/conf/<cid>", methods=['DELETE'])
def deleteScrapingConf(cid):
    """ 删除配置
    """
    try:
        iid = int(cid)
        scrapingConfService.deleteConf(iid)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/record", methods=['DELETE'])
def deleteScrapingRecordIds():
    try:
        content = request.get_json()
        scrapingrecordService.deleteByIds(content.get('ids'), content.get('delsrc'))
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/record", methods=['GET'])
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
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scraping/record", methods=['PUT'])
def editScrapingData():
    try:
        content = request.get_json()
        scrapingrecordService.editRecord(content['id'],
                                         content['status'],
                                         content['scrapingname'],
                                         content['cnsubtag'],
                                         content['leaktag'],
                                         content['uncensoredtag'],
                                         content['hacktag'],
                                         content['cdnum'])
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
