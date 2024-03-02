# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from sqlalchemy import or_, asc, desc
from ..model.record import _ScrapingRecords, _TransRecords
from ..utils.filehelper import checkFileExists, cleanFolderbyFilter, cleanFilebyFilter, cleanExtraMedia, cleanFolderWithoutSuffix, video_type
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
            self.commit()
        return info

    def queryByPath(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(srcpath=value).first()

    def queryLatest(self, value):
        infos = _ScrapingRecords.query.filter(_ScrapingRecords.srcpath.like("%" + value + "%")).all()
        return infos

    def queryByID(self, value) -> _ScrapingRecords:
        return _ScrapingRecords.query.filter_by(id=value).first()

    @staticmethod
    def deleteRecordFiles(record: _ScrapingRecords, delsrc=False):
        """ 删除关联的实际文件
        """
        basefolder = os.path.dirname(record.srcpath)
        if delsrc and os.path.exists(basefolder):
            srcname = os.path.basename(record.srcpath)
            srcfilter = os.path.splitext(srcname)[0]
            cleanFilebyFilter(basefolder, srcfilter)
        if record.destpath and record.destpath != '':
            folder = os.path.dirname(record.destpath)
            if os.path.exists(folder) and basefolder != folder:
                name = os.path.basename(record.destpath)
                filter = os.path.splitext(name)[0]
                if record.cdnum and record.cdnum > 0:
                    cleanFilebyFilter(folder, filter)
                else:
                    cleanFolderbyFilter(folder, filter)

    def deleteByIds(self, ids, delsrc=False):
        delrecords = []
        records = _ScrapingRecords.query.filter(_ScrapingRecords.id.in_(ids)).all()
        for record in records:
            self.deleteRecordFiles(record, delsrc)
            self.deleteRecord(record, delsrc)
            delrecords.append(record.srcpath)
        self.commit()
        return delrecords

    def cleanUnavailable(self):
        records = _ScrapingRecords.query.all()
        for i in records:
            if i.linktype == 0:
                if not os.path.exists(i.destpath):
                    self.deleteRecordFiles(i, False)
                    self.deleteRecord(i)
            else:
                if not os.path.exists(i.srcpath) or not os.path.exists(i.destpath):
                    self.deleteRecordFiles(i, False)
                    self.deleteRecord(i)
        self.commit()

    def deadtimetoMissingrecord(self) -> list:
        """ 源文件或目标文件不存在，全部删除
        """
        delrecords = []
        records = _ScrapingRecords.query.all()
        for i in records:
            # 排除忽略标记
            if not i.ignored:
                # 已标记deadtime，检查是否到期，进行删除
                if i.deadtime:
                    nowtime = datetime.datetime.now()
                    if nowtime > i.deadtime:
                        self.deleteRecordFiles(i, True)
                        self.deleteRecord(i)
                        delrecords.append(i.srcpath)
                        continue
                # 0 转移 1 软链接 2 硬链接
                if i.linktype == 0:
                    # 转移必须是文件实体
                    if not os.path.exists(i.destpath):
                        if not i.deadtime or i.deadtime == '':
                            i.deadtime = datetime.datetime.now() + datetime.timedelta(days=7)
                    else:
                        # 曾经标记过，但现在已经恢复，则取消删除计划
                        if i.deadtime:
                            i.deadtime = None
                else:
                    if os.path.exists(i.srcpath) and checkFileExists(i.destpath):
                        # 曾经标记过，但现在已经恢复，则取消删除计划
                        if i.deadtime:
                            i.deadtime = None
                    else:
                        if not i.deadtime or i.deadtime == '':
                            i.deadtime = datetime.datetime.now() + datetime.timedelta(days=7)

        self.commit()
        return delrecords

    def editRecord(self, sid, status, scrapingname,
                   ignored, locked,
                   specifiedsource, specifiedurl,
                   cnsubtag, leaktag, uncensoredtag, hacktag, cdnum, deadtime):
        info = _ScrapingRecords.query.filter_by(id=sid).first()
        if info:
            if locked:
                if not info.locked:
                    info.ignored = False
                    info.locked = True
                    info.deadtime = None
                    self.updateRecord(info, status, scrapingname, specifiedsource, specifiedurl,
                                      cnsubtag, leaktag, uncensoredtag, hacktag, cdnum, deadtime)
            elif ignored:
                if not info.ignored:
                    info.ignored = True
                    info.locked = False
                    info.deadtime = None
                    self.deleteRecordFiles(info, False)
                    status = 3
                    info.destpath = info.destname = ""
                    self.updateRecord(info, status, scrapingname, specifiedsource, specifiedurl,
                                      cnsubtag, leaktag, uncensoredtag, hacktag, cdnum, deadtime)
            else:
                info.ignored = False
                info.locked = False
                self.updateRecord(info, status, scrapingname, specifiedsource, specifiedurl,
                                  cnsubtag, leaktag, uncensoredtag, hacktag, cdnum, deadtime)

    def updateRecord(self, record: _ScrapingRecords, status, scrapingname,
                     specifiedsource, specifiedurl,
                     cnsubtag, leaktag, uncensoredtag, hacktag, cdnum, deadtime):
        record.status = status
        record.scrapingname = scrapingname
        record.specifiedsource = specifiedsource
        record.specifiedurl = specifiedurl
        record.cnsubtag = cnsubtag
        record.leaktag = leaktag
        record.uncensoredtag = uncensoredtag
        record.hacktag = hacktag
        if not cdnum or cdnum == '':
            cdnum = 0
        record.cdnum = int(cdnum)
        record.updatetime = datetime.datetime.now()
        if deadtime == '' and record.deadtime:
            record.deadtime = None
        self.commit()

    def deleteRecord(self, record, forced=False):
        """ 删除记录
        :param forced   True: 删除记录 False: 仅做标记
        """
        if forced:
            db.session.delete(record)
        else:
            record.deleted = True

    def updateDeleted(self, record: _ScrapingRecords):
        record.deleted = True
        record.status = 3
        record.updatetime = datetime.datetime.now()
        self.commit()

    def commit(self):
        db.session.commit()

    def queryByPage(self, pagenum, pagesize, status, sortprop, sortorder, blur):
        """ 查询
        """
        direction = asc if sortorder == 'ascending' else desc
        sortname = sortprop if sortprop else 'updatetime'
        sortattr = getattr(_ScrapingRecords, sortname)
        if blur:
            filterparam = or_(_ScrapingRecords.srcname.like("%" + blur + "%"),
                              _ScrapingRecords.scrapingname.like("%" + blur + "%"),
                              _ScrapingRecords.destname.like("%" + blur + "%"))
            infos = _ScrapingRecords.query.filter(filterparam).order_by(
                direction(sortattr)).paginate(page=pagenum, per_page=pagesize, error_out=False)
        else:
            infos = _ScrapingRecords.query.order_by(direction(sortattr)).paginate(
                page=pagenum, per_page=pagesize, error_out=False)
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
            self.commit()
            return info
        return info

    def queryByID(self, value) -> _TransRecords:
        info = _TransRecords.query.filter_by(id=value).first()
        if not info:
            return None
        return info

    def queryByPath(self, value) -> _TransRecords:
        info = _TransRecords.query.filter_by(srcpath=value).first()
        if not info:
            return None
        return info

    def queryLatest(self, value):
        infos = _TransRecords.query.filter(_TransRecords.srcpath.like("%" + value + "%")).all()
        return infos

    def editRecord(self, info: _TransRecords, softpath, destpath,
                   status, ignored, locked,
                   topfolder, secondfolder,
                   isepisode, season, epnum,
                   renameTop_tag=False, renameSub_tag=False, deadtime=None):
        """ 由API调用编辑
        """
        if info:
            if topfolder == '':
                topfolder = '.'
            if renameTop_tag and topfolder != '.':
                self.renameAllTop(info.srcfolder, info.topfolder, topfolder)
            if isepisode:
                if renameSub_tag:
                    self.renameAllSeason(info.srcfolder, info.topfolder, info.secondfolder, info.season, season)
            else:
                if renameSub_tag:
                    self.renameAllSecond(info.srcfolder, info.topfolder, info.secondfolder, secondfolder)
            if deadtime == '' and info.deadtime:
                info.deadtime = None
            if locked:
                if not info.locked:
                    info.ignored = False
                    info.locked = True
                    info.deadtime = None
                    self.updateRecord(info, softpath, destpath, status, topfolder, secondfolder,
                                      isepisode, season, epnum)
            elif ignored:
                if not info.ignored:
                    info.ignored = True
                    info.locked = False
                    info.deadtime = None
                    self.deleteRecordFiles(info, False)
                    status = 3
                    softpath = destpath = ""
                    topfolder = secondfolder = ""
                    isepisode = False
                    self.updateRecord(info, softpath, destpath, status, topfolder, secondfolder,
                                      isepisode, season, epnum)
            else:
                info.ignored = False
                info.locked = False
                self.updateRecord(info, softpath, destpath, status, topfolder, secondfolder,
                                  isepisode, season, epnum)

    def updateRecord(self, info: _TransRecords, softpath, destpath,
                     status, topfolder, secondfolder,
                     isepisode, season, epnum):
        """ 由转移任务更新
        """
        if info:
            info.linkpath = softpath
            info.destpath = destpath
            info.status = status
            if topfolder == '':
                topfolder = '.'
            info.topfolder = topfolder
            info.secondfolder = secondfolder
            if isepisode:
                info.isepisode = True
                info.season = season
                info.episode = epnum
            else:
                info.isepisode = False
                info.season = -1
                info.episode = -1
            info.updatetime = datetime.datetime.now()
            self.commit()

    def deleteRecord(self, record, forced=False):
        """ 删除记录
        :param forced   True: 删除记录 False: 仅做标记
        """
        if forced:
            db.session.delete(record)
        else:
            record.deleted = True

    def commit(self):
        db.session.commit()

    def queryByPage(self, pagenum, pagesize, status, sortprop, sortorder, blur):
        direction = asc if sortorder == 'ascending' else desc
        sortname = sortprop if sortprop else 'updatetime'
        sortattr = getattr(_TransRecords, sortname)
        if blur:
            filterparam = or_(_TransRecords.srcname.like("%" + blur + "%"),
                              _TransRecords.destpath.like("%" + blur + "%"),
                              _TransRecords.topfolder.like("%" + blur + "%"))
            infos = _TransRecords.query.filter(filterparam).order_by(
                direction(sortattr)).paginate(page=pagenum, per_page=pagesize, error_out=False)
        else:
            infos = _TransRecords.query.order_by(direction(sortattr)).paginate(
                page=pagenum, per_page=pagesize, error_out=False)
        return infos

    @staticmethod
    def deleteRecordFiles(record: _TransRecords, delsrc):
        """ 删除关联的实际文件
        :param delsrc   是否删除原始文件
        """
        basefolder = os.path.dirname(record.srcpath)
        if delsrc and os.path.exists(basefolder):
            srcname = os.path.basename(record.srcpath)
            srcfilter = os.path.splitext(srcname)[0]
            cleanFilebyFilter(basefolder, srcfilter)
        if record.destpath != '':
            folder = os.path.dirname(record.destpath)
            if os.path.exists(folder) and basefolder != folder:
                name = os.path.basename(record.destpath)
                # 前缀匹配
                filter = os.path.splitext(name)[0]
                cleanFilebyFilter(folder, filter)
        if record.topfolder != '.':
            cleanfolder = os.path.dirname(record.destpath)
            if record.secondfolder:
                cleanfolder = os.path.dirname(cleanfolder)
            if os.path.exists(cleanfolder):
                cleanFolderWithoutSuffix(cleanfolder, video_type)

    def deleteByIds(self, ids, delsrc=False):
        delrecords = []
        records = _TransRecords.query.filter(_TransRecords.id.in_(ids)).all()
        for record in records:
            self.deleteRecordFiles(record, delsrc)
            self.deleteRecord(record, delsrc)
            delrecords.append(record.srcpath)
        self.commit()
        return delrecords

    def cleanUnavailable(self):
        records = _TransRecords.query.all()
        for i in records:
            if not os.path.exists(i.srcpath) or not os.path.exists(i.destpath):
                self.deleteRecordFiles(i, False)
                self.deleteRecord(i)
        self.commit()

    def deadtimetoMissingrecord(self) -> list:
        delrecords = []
        records = _TransRecords.query.all()
        for i in records:
            # 忽略标记
            if not i.ignored:
                # 已标记deadtime，检查是否到期，进行删除
                if i.deadtime:
                    nowtime = datetime.datetime.now()
                    if nowtime > i.deadtime:
                        self.deleteRecordFiles(i, True)
                        self.deleteRecord(i)
                        delrecords.append(i.srcpath)
                        continue
                # 0 软链接 1 硬链接
                if os.path.exists(i.srcpath) and checkFileExists(i.destpath):
                    if i.deadtime:
                        # 曾经标记过，但现在已经恢复，则取消删除计划
                        i.deadtime = None
                else:
                    if not i.deadtime or i.deadtime == '':
                        i.deadtime = datetime.datetime.now() + datetime.timedelta(days=7)
        self.commit()
        return delrecords

    def renameAllTop(self, srcfolder, top, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top).all()
        for single in records:
            if not single.ignored and not single.locked:
                single.topfolder = new
                single.updatetime = datetime.datetime.now()

    def renameAllSecond(self, srcfolder, top, second, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top, secondfolder=second).all()
        for single in records:
            if not single.ignored and not single.locked:
                single.secondfolder = new
                single.updatetime = datetime.datetime.now()

    def renameAllSeason(self, srcfolder, top, second, season, new):
        records = _TransRecords.query.filter_by(srcfolder=srcfolder, topfolder=top,
                                                secondfolder=second, season=season).all()
        for single in records:
            if not single.ignored and not single.locked:
                single.isepisode = True
                single.season = new
                single.updatetime = datetime.datetime.now()


scrapingrecordService = ScrapingRecordService()
transrecordService = TransRecordService()
