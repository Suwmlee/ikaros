# -*- coding: utf-8 -*-


import json
from flask import request, Response, current_app

from . import web
from ..bizlogic.transfer import ctrlTransfer
from ..bizlogic.schedulertask import cleanTorrents
from ..service.configservice import localConfService, transConfigService
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService


@web.route("/api/transfer", methods=['POST'])
def startTransfer():
    content = request.get_json()
    ctrlTransfer(
        content["source_folder"],
        content["output_folder"],
        content["linktype"],
        content["soft_prefix"],
        content["escape_folder"],
        content.get("specified_files"),
        content["fix_series"],
        content["clean_others"],
        content["replace_CJK"],
        content.get("refresh_url"),
        content["is_sym_relative_path"],
    )
    return Response(status=200)


@web.route("/api/transfer/conf/all", methods=['GET'])
def getTransConfs():
    """ 查询转移配置
    """
    configs = transConfigService.getConfiglist()
    all = []
    for conf in configs:
        all.append(conf.serialize())
    return json.dumps(all)


@web.route("/api/transfer/conf", methods=['POST'])
def addTransConf():
    """ 新增转移配置
    """
    content = request.get_json()
    content['id'] = None
    config = transConfigService.updateConf(content)
    return json.dumps(config.serialize())


@web.route("/api/transfer/conf", methods=['PUT'])
def updateTransConf():
    """ 更新转移配置
    """
    content = request.get_json()
    config = transConfigService.updateConf(content)
    return json.dumps(config.serialize())


@web.route("/api/transfer/conf/<cid>", methods=['DELETE'])
def deleteTransConf(cid):
    """ 删除转移配置
    """
    iid = int(cid)
    transConfigService.deleteConf(iid)
    return Response(status=200)

# record


@web.route("/api/transfer/record", methods=['GET'])
def getTransRecord():
    """ 查询
    """
    pagenum = int(request.args.get('page'))
    size = int(request.args.get('size'))
    status = request.args.get('status')
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

    infos = transrecordService.queryByPage(pagenum, size, status, sortprop, sortorder, blur)
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


@web.route("/api/transfer/record", methods=['PUT'])
def editTransferRecord():
    content = request.get_json()
    info = transrecordService.queryByPath(content.get('srcpath'))
    transrecordService.editRecord(info, content.get('linkpath'), content.get('destpath'),
                              content.get('status'), content.get('ignored'), content.get('locked'), 
                              content.get('topfolder'), content.get('secondfolder'), content.get('forcedname'),
                              content.get('isepisode'), content.get('season'), content.get('episode'),
                              content.get('renameAllTop'), content.get('renameAllSub'), content.get('deadtime'))
    return Response(status=200)


@web.route("/api/transfer/record", methods=['DELETE'])
def deleteTransferRecordIds():
    content = request.get_json()
    ids = content.get('ids')
    delsrc = content.get('delsrc')
    delrecords = transrecordService.deleteByIds(ids, delsrc)
    if delsrc:
        localconfig = localConfService.getConfig()
        cleanTorrents(delrecords, localconfig)
    return Response(status=200)
