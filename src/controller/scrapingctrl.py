# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app
from . import web
from ..service.recordservice import scrapingrecordService


@web.route("/api/scraping/record", methods=['DELETE'])
def deleteScrapingRecordIds():
    try:
        ids = request.get_json()
        scrapingrecordService.deleteByIds(ids)
        # for sid in ids:
        #     scrapingrecordService.deleteByID(sid)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/scrapingrecord", methods=['PUT'])
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
