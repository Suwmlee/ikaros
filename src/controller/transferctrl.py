# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app
from . import web
from ..bizlogic import transfer
from ..service.configservice import transConfigService
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService


@web.route("/api/transfer", methods=['POST'])
def startTransfer():
    try:
        content = request.get_json()
        transfer.ctrlTransfer(content['source_folder'], content['output_folder'],
                              content['linktype'], content['soft_prefix'],
                              content['escape_folder'], content.get('specified_files'),
                              content['fix_series'],
                              content['clean_others'], content['replace_CJK'],
                              content.get('refresh_url'))
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/conf/all", methods=['GET'])
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
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/conf", methods=['POST'])
def addTransConf():
    """ 新增转移配置
    """
    try:
        content = request.get_json()
        content['id'] = None
        config = transConfigService.updateConf(content)
        return json.dumps(config.serialize())
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/conf", methods=['PUT'])
def updateTransConf():
    """ 更新转移配置
    """
    try:
        content = request.get_json()
        config = transConfigService.updateConf(content)
        return json.dumps(config.serialize())
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/conf/<cid>", methods=['DELETE'])
def deleteTransConf(cid):
    """ 删除转移配置
    """
    try:
        iid = int(cid)
        transConfigService.deleteConf(iid)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)

# record

@web.route("/api/transfer/record", methods=['GET'])
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
        info = transrecordService.queryByPath(content.get('srcpath'))
        transrecordService.update(info, content.get('linkpath'), content.get('destpath'),
                                    content.get('status'), content.get('topfolder'), content.get('secondfolder'),
                                    content.get('isepisode'), content.get('season'), content.get('episode'),
                                    content.get('renameAllTop'), content.get('renameAllSub'))
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/transfer/record", methods=['DELETE'])
def deleteTransferRecordIds():
    try:
        content = request.get_json()
        ids = content.get('ids')
        delsrc = content.get('delsrc')
        for sid in ids:
            transrecordService.deleteByID(sid, delsrc)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
