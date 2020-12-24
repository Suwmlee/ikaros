# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from ..model.info import _Info, _TransferLog
from .. import db


class InfoService():

    def addInfo(self, path):
        info = self.getInfoByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            info = _Info(name, path)
            db.session.add(info)
            db.session.commit()
            return info
        return info

    def getInfoByPath(self, value) -> _Info:
        return _Info.query.filter_by(basepath=value).first()

    def updateInfo(self, path, newpath, flag):
        info = self.getInfoByPath(path)
        if info:
            if flag:
                (filefolder, newname) = os.path.split(newpath)
                info.status = 1
                info.newname = newname
                info.newpath = newpath
            else:
                info.status = 2
            info.updatetime = datetime.datetime.now()
            db.session.commit()
        return info

class TransferService():

    def addTransferLog(self, path):
        info = self.getTransferLogByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            info = _TransferLog(name, path)
            db.session.add(info)
            db.session.commit()
            return info
        return info

    def getTransferLogByPath(self, value):
        info = _TransferLog.query.filter_by(basepath=value).first()
        if not info:
            return None
        return info

    def updateTransferLog(self, path, softpath, destpath):
        info = self.getTransferLogByPath(path)
        if info:
            info.success = True
            info.softpath = softpath
            info.destpath = destpath
            info.updatetime = datetime.datetime.now()
            db.session.commit()


infoService = InfoService()
transferService = TransferService()
