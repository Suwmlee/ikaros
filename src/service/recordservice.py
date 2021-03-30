# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from ..model.record import _ScrapingRecords, _TransRecords
from .. import db


class ScrapingRecordService():

    def add(self, path):
        info = self.queryByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            size = os.path.getsize(path) >> 20
            info = _ScrapingRecords(name, path)
            info.srcsize = size
            db.session.add(info)
            db.session.commit()
        return info

    def queryAll(self):
        return _ScrapingRecords.query.all()

    def queryByPath(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(basepath=value).first()

    def getRecordByID(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(id=value).first()

    def update(self, path, sname, newpath, flag):
        info = self.queryByPath(path)
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

    def queryByPage(self, pagenum, pagesize, sort):
        infos = _ScrapingRecords.query.order_by(_ScrapingRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos

class TransRecordService():

    def add(self, path):
        info = self.queryByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            size = os.path.getsize(path) >> 20
            info = _TransRecords(name, path)
            info.srcsize = size
            db.session.add(info)
            db.session.commit()
            return info
        return info

    def queryByPath(self, value):
        info = _TransRecords.query.filter_by(basepath=value).first()
        if not info:
            return None
        return info

    def update(self, path, softpath, destpath):
        info = self.queryByPath(path)
        if info:
            info.success = True
            info.softpath = softpath
            info.destpath = destpath
            info.updatetime = datetime.datetime.now()
            db.session.commit()
    
    def queryByPage(self, pagenum, pagesize, sort):
        infos = _TransRecords.query.order_by(_TransRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos


scrapingrecordService = ScrapingRecordService()
transrecordService = TransRecordService()
