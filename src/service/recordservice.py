# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from sqlalchemy import or_
from ..model.record import _ScrapingRecords, _TransRecords
from ..utils.filehelper import cleanFolderbyFilter, cleanScrapingfile
from .. import db


class ScrapingRecordService():

    def add(self, path) -> _ScrapingRecords:
        """ 优先查询已有数据
        存在则返回，不存在则新增
        """
        info = self.queryByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            if os.path.exists(path):
                size = os.path.getsize(path) >> 20
            else:
                size = 0
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
            if record.destpath != '':
                basefolder = os.path.dirname(record.srcpath)
                folder = os.path.dirname(record.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(record.destpath)
                    filter  = os.path.splitext(name)[0]
                    if record.cdnum and record.cdnum > 0:
                        cleanScrapingfile(folder, filter)
                    else:
                        cleanFolderbyFilter(folder, filter)
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

    def editRecord(self, sid, status, scrapingname, cnsubtag, cdnum):
        record = _ScrapingRecords.query.filter_by(id=sid).first()
        if record:
            record.status = status
            record.scrapingname = scrapingname
            record.cnsubtag = cnsubtag
            record.cdnum = cdnum
            record.updatetime = datetime.datetime.now()
            db.session.commit()

    def commit(self):
        db.session.commit()

    def queryByPage(self, pagenum, pagesize, sortprop, sortorder, blur):
        """ 查询
        """
        if sortprop == 'status':
            if sortorder == 'ascending':
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.status.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.status.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        elif sortprop == 'cnsubtag':
            if sortorder == 'ascending':
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.cnsubtag.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.cnsubtag.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        else:
            if sortorder == 'ascending':
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.updatetime.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                infos = _ScrapingRecords.query.filter(
                    or_(_ScrapingRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.scrapingname.like("%" + blur + "%") if blur is not None else "",
                        _ScrapingRecords.destname.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_ScrapingRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
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

    def update(self, path, softpath, destpath, status, 
                topfolder, secondfolder,
                isepisode, season, epnum, 
                renameTop_tag = False, renameSub_tag = False):
        info = self.queryByPath(path)
        if info:
            info.linkpath = softpath
            info.destpath = destpath
            info.status = status
            if topfolder == '':
                topfolder = '.'
            if renameTop_tag and topfolder != '.':
                self.renameAllTop(info.srcfolder, info.topfolder, topfolder)
            info.topfolder = topfolder
            if isepisode:
                if renameSub_tag:
                    self.renameAllSeason(info.srcfolder, info.topfolder, info.season, season)
                else:
                    info.isepisode = True
                    info.season = season
                info.episode = epnum
            else:
                if renameSub_tag:
                    self.renameAllSecond(info.srcfolder, info.topfolder, info.secondfolder, secondfolder)
                else:
                    info.secondfolder = secondfolder
            info.updatetime = datetime.datetime.now()
            db.session.commit()

    def queryByPage(self, pagenum, pagesize, sort, blur):
        infos = _TransRecords.query.filter(
                    or_(_TransRecords.srcname.like("%" + blur + "%") if blur is not None else "",
                        _TransRecords.destpath.like("%" + blur + "%") if blur is not None else "",
                        _TransRecords.topfolder.like("%" + blur + "%") if blur is not None else "")
                ).order_by(_TransRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos

    def deleteRecords(self):
        nums  = _TransRecords.query.delete()
        db.session.commit()
        return nums

    def deleteByID(self, value) -> _TransRecords:
        record = _TransRecords.query.filter_by(id=value).first()
        if record:
            if record.destpath != '':
                basefolder = os.path.dirname(record.srcpath)
                folder = os.path.dirname(record.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(record.destpath)
                    # 前缀匹配
                    filter  = os.path.splitext(name)[0]
                    cleanScrapingfile(folder, filter)
            db.session.delete(record)
            db.session.commit()

    def renameAllTop(self, srcfolder, top, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top).all()
        for single in records:
            if single.status != 1 and single.status != 2:
                single.topfolder = new
                single.updatetime = datetime.datetime.now()

    def renameAllSecond(self, srcfolder, top, second, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top, secondfolder=second).all()
        for single in records:
            if single.status != 1 and single.status != 2:
                single.secondfolder = new
                single.updatetime = datetime.datetime.now()

    def renameAllSeason(self, srcfolder, top, season, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top, season=season).all()
        for single in records:
            if single.status != 1 and single.status != 2:
                single.isepisode = True
                single.season = new
                single.updatetime = datetime.datetime.now()


scrapingrecordService = ScrapingRecordService()
transrecordService = TransRecordService()
