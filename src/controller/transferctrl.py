# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app
from . import web
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService


@web.route("/api/transfer/record", methods=['DELETE'])
def deleteTransferRecordIds():
    try:
        ids = request.get_json()
        for sid in ids:
            transrecordService.deleteByID(sid)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transrecord", methods=['GET'])
def getTransRecord():
    """ 查询
    """
    try:
        pagenum = int(request.args.get('page'))
        size = int(request.args.get('size'))
        sort = 0
        blur = request.args.get('blur')
        infos = transrecordService.queryByPage(pagenum, size, sort, blur)
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
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/record", methods=['PUT'])
def editTransferRecord():
    try:
        content = request.get_json()
        transrecordService.update(content.get('srcpath'), content.get('linkpath'), content.get('destpath'),
                                      content.get('topfolder'), content.get('secondfolder'),
                                      content.get('isepisode'), content.get('season'), content.get('episode'))
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
