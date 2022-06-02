# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from sqlalchemy import or_
from ..model.record import _ScrapingRecords, _TransRecords
from ..utils.filehelper import cleanFolderbyFilter, cleanFilebyFilter, cleanExtraMedia, cleanFolderWithoutSuffix, video_type
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

    def queryLatest(self, value):
        infos = _ScrapingRecords.query.filter(_ScrapingRecords.srcpath.like("%" + value + "%")).all()
        return infos

    def queryByID(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(id=value).first()

    def deleteByID(self, value):
        record = _ScrapingRecords.query.filter_by(id=value).first()
        if record:
            if record.destpath != '':
                basefolder = os.path.dirname(record.srcpath)
                folder = os.path.dirname(record.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(record.destpath)
                    filter  = os.path.splitext(name)[0]
                    if record.cdnum and record.cdnum > 0:
                        cleanFilebyFilter(folder, filter)
                    else:
                        cleanFolderbyFilter(folder, filter)
            db.session.delete(record)
            db.session.commit()

    def deleteByIds(self, ids, delsrc=False):
        records = _ScrapingRecords.query.filter(_ScrapingRecords.id.in_(ids)).all()
        for record in records:
            basefolder = os.path.dirname(record.srcpath)
            if delsrc:
                srcname = os.path.basename(record.srcpath)
                srcfilter  = os.path.splitext(srcname)[0]
                cleanFilebyFilter(basefolder, srcfilter)
            if record.destpath != '':
                folder = os.path.dirname(record.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(record.destpath)
                    filter  = os.path.splitext(name)[0]
                    if record.cdnum and record.cdnum > 0:
                        cleanFilebyFilter(folder, filter)
                    else:
                        cleanFolderbyFilter(folder, filter)
            db.session.delete(record)
        db.session.commit()

    def cleanUnavailable(self):
        records = self.queryAll()
        for i in records:
            srcpath = i.srcpath
            dstpath = i.destpath
            if not os.path.exists(srcpath):
                if i.linktype == 1:
                    self.deleteByID(i.id)
                if not os.path.exists(dstpath):
                    self.deleteByID(i.id)

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

    def editRecord(self, sid, status, scrapingname, cnsubtag, leaktag, uncensoredtag, hacktag, cdnum):
        record = _ScrapingRecords.query.filter_by(id=sid).first()
        if record:
            record.status = status
            record.scrapingname = scrapingname
            record.cnsubtag = cnsubtag
            record.leaktag = leaktag
            record.uncensoredtag = uncensoredtag
            record.hacktag = hacktag
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
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.status.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
                    infos = _ScrapingRecords.query.order_by(_ScrapingRecords.status.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.status.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
                    infos = _ScrapingRecords.query.order_by(_ScrapingRecords.status.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        elif sortprop == 'cnsubtag':
            if sortorder == 'ascending':
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.cnsubtag.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
                    infos = _ScrapingRecords.query.order_by(_ScrapingRecords.cnsubtag.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.cnsubtag.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
                    infos = _ScrapingRecords.query.order_by(_ScrapingRecords.cnsubtag.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        else:
            if sortorder == 'ascending':
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.updatetime.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
                    infos = _ScrapingRecords.query.order_by(_ScrapingRecords.updatetime.asc()).paginate(pagenum, per_page=pagesize, error_out=False)
            else:
                if blur:
                    infos = _ScrapingRecords.query.filter(
                        or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                            _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                            _ScrapingRecords.destname.like("%" + blur + "%"))
                    ).order_by(_ScrapingRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
                else:
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

    def queryLatest(self, value):
        infos = _TransRecords.query.filter(_TransRecords.srcpath.like("%" + value + "%")).all()
        return infos

    def update(self, info: _TransRecords, softpath, destpath, status, 
                topfolder, secondfolder,
                isepisode, season, epnum, 
                renameTop_tag = False, renameSub_tag = False):
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
                    self.renameAllSeason(info.srcfolder, info.topfolder, info.secondfolder, info.season, season)
                else:
                    info.isepisode = True
                    info.season = season
                info.episode = epnum
                info.secondfolder = secondfolder
            else:
                info.isepisode = False
                if renameSub_tag:
                    self.renameAllSecond(info.srcfolder, info.topfolder, info.secondfolder, secondfolder)
                else:
                    info.secondfolder = secondfolder
            info.updatetime = datetime.datetime.now()
            db.session.commit()

    def queryByPage(self, pagenum, pagesize, sort, blur):
        if blur:
            infos = _TransRecords.query.filter(
                        or_(_TransRecords.srcname.like("%" + blur + "%"),
                            _TransRecords.destpath.like("%" + blur + "%"),
                            _TransRecords.topfolder.like("%" + blur + "%"))
                    ).order_by(_TransRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        else:
            infos = _TransRecords.query.order_by(_TransRecords.updatetime.desc()).paginate(pagenum, per_page=pagesize, error_out=False)
        return infos

    def deleteRecords(self):
        nums  = _TransRecords.query.delete()
        db.session.commit()
        return nums

    def deleteByID(self, value, delsrc=False) -> _TransRecords:
        record = _TransRecords.query.filter_by(id=value).first()
        if record and isinstance(record, _TransRecords):
            basefolder = os.path.dirname(record.srcpath)
            if delsrc:
                srcname = os.path.basename(record.srcpath)
                srcfilter  = os.path.splitext(srcname)[0]
                cleanFilebyFilter(basefolder, srcfilter)
            if record.destpath != '':
                folder = os.path.dirname(record.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(record.destpath)
                    # 前缀匹配
                    filter = os.path.splitext(name)[0]
                    cleanFilebyFilter(folder, filter)
            db.session.delete(record)
            db.session.commit()

            if record.topfolder != '.':
                cleanfolder = os.path.dirname(record.destpath)
                if record.secondfolder:
                    cleanfolder = os.path.dirname(cleanfolder)
                if os.path.exists(cleanfolder):
                    cleanFolderWithoutSuffix(cleanfolder, video_type)

    def cleanUnavailable(self):
        records = _TransRecords.query.all()
        for i in records:
            srcpath = i.srcpath
            dstpath = i.destpath
            if not os.path.exists(srcpath) or not os.path.exists(dstpath):
                self.deleteByID(i.id)

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

    def renameAllSeason(self, srcfolder, top, second, season, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top, 
                                                secondfolder=second, season=season).all()
        for single in records:
            if single.status != 1 and single.status != 2:
                single.isepisode = True
                single.season = new
                single.updatetime = datetime.datetime.now()


scrapingrecordService = ScrapingRecordService()
transrecordService = TransRecordService()
