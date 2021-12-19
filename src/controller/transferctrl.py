# -*- coding: utf-8 -*-


from flask import request, Response, current_app
from . import web
from ..service.recordservice import transrecordService


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
