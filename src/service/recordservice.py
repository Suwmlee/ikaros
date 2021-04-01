# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from ..model.record import _ScrapingRecords, _TransRecords
from .. import db


class ScrapingRecordService():

    def add(self, path) -> _ScrapingRecords:
        info = self.queryByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            if os.path.exists(path):
                size = os.path.getsize(path) >> 20
            info = _ScrapingRecords(name, path)
            info.srcsize = size
            db.session.add(info)
            db.session.commit()
        return info

    def queryAll(self):
        return _ScrapingRecords.query.all()

    def queryByPath(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(srcpath=value).first()

    def queryByID(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(id=value).first()

    def deleteByID(self, value) -> _ScrapingRecords:
        record = _ScrapingRecords.query.filter_by(id=value).first()
        if record:
            db.session.delete(record)
            db.session.commit()

    def importRecord(self, name, path, size, status):
        record = _ScrapingRecords.query.filter_by(srcpath=path).first()
        if not record:
            record = _ScrapingRecords(name, path)
            record.srcsize = size
            record.status = status
            db.session.add(record)
        else:
            record.srcsize = size
            record.status = status
        db.session.commit()

    def editRecord(self, sid, status, scrapingname):
        record = _ScrapingRecords.query.filter_by(id=sid).first()
        if record:
            record.status = status
            record.scrapingname = scrapingname
            record.updatetime = datetime.datetime.now()
            db.session.commit()

    def update(self, path, sname, newpath, flag):
        info = self.queryByPath(path)
        if info:
            if flag:
                (filefolder, newname) = os.path.split(newpath)
                info.status = 1
                info.destname = newname
                info.destpath = newpath
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

    def add(self, path) -> _TransRecords:
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

    def queryByPath(self, value) -> _TransRecords:
        info = _TransRecords.query.filter_by(srcpath=value).first()
        if not info:
            return None
        return info

    def update(self, path, softpath, destpath):
        info = self.queryByPath(path)
        if info:
            info.success = True
            info.linkpath = softpath
            info.destpath = destpath
            info.updatetime = datetime.datetime.now()
            db.session.commit()

    def queryByPage(self, pagenum, pagesize, sort):
        infos = _TransRecords.query.order_by(_TransRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos


scrapingrecordService = ScrapingRecordService()
transrecordService = TransRecordService()
