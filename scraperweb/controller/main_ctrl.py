
import json
import os
import datetime
from time import sleep
from threading import Lock
from flask import render_template, request, Response

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..service.info import infoService, transferService
from ..service.setting import settingService
from ..service.task import taskService
from ..utils.wlogger import wlogger
# from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
# executor = ThreadPoolExecutor(2)


@web.route("/api/scrape", methods=['POST'])
def start_scraper():
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
        transfer.transfer(content['source_folder'], content['output_folder'], content['soft_prefix'], content['escape_folder'])
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/scrapedata/<page>", methods=['GET'])
def get_scrape(page):
    try:
        pagenum = int(page)
        size = 10
        sort = 0
        infos = infoService.getInfoPage(pagenum, size, sort)
        data = []
        for i in infos.items:
            data.append(i.serialize())
        ret = dict()
        ret['data'] = data
        ret['total'] = infos.total
        ret['pages'] = infos.pages
        ret['page'] = pagenum
        if taskService.getTask('scrape').status == 2:
            ret['running'] = True
        else:
            ret['running'] = False
        return json.dumps(ret)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/transferdata/<page>", methods=['GET'])
def get_transfer(page):
    try:
        pagenum = int(page)
        size = 10
        sort = 0
        infos = transferService.getLogPage(pagenum, size, sort)
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


@web.route("/api/setting", methods=['GET'])
def getSetting():
    try:
        content = settingService.getSetting().serialize()
        return json.dumps(content)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/setting", methods=['POST'])
def updateSetting():
    try:
        content = request.get_json()
        settingService.updateSetting(content)
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)
