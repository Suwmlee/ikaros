# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from ..model.log import _ScrapingLog, _TransLog
from .. import db


class ScrapingLogService():

    def addInfo(self, path):
        info = self.getInfoByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            size = os.path.getsize(path) >> 20
            info = _ScrapingLog(name, path)
            info.filesize = size
            db.session.add(info)
            db.session.commit()
        return info

    def getInfoByPath(self, value) -> _ScrapingLog:
        return _ScrapingLog.query.filter_by(basepath=value).first()

    def updateInfo(self, path, sname, newpath, flag):
        info = self.getInfoByPath(path)
        if info:
            if flag:
                (filefolder, newname) = os.path.split(newpath)
                info.status = 1
                info.newname = newname
                info.newpath = newpath
            else:
                info.status = 2
            info.scrapingname = sname
            info.updatetime = datetime.datetime.now()
            db.session.commit()
        return info

    def getInfoPage(self, pagenum, pagesize, sort):
        infos = _ScrapingLog.query.order_by(_ScrapingLog.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos

class TransLogService():

    def addTransferLog(self, path):
        info = self.getTransferLogByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            size = os.path.getsize(path) >> 20
            info = _TransLog(name, path)
            info.filesize = size
            db.session.add(info)
            db.session.commit()
            return info
        return info

    def getTransferLogByPath(self, value):
        info = _TransLog.query.filter_by(basepath=value).first()
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
    
    def getLogPage(self, pagenum, pagesize, sort):
        infos = _TransLog.query.order_by(_TransLog.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos


scrapinglogService = ScrapingLogService()
translogService = TransLogService()
