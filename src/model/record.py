# -*- coding: utf-8 -*-
"""
    刮削/转移记录
    关键参数:
    status:
        0   等待
        1   成功
        2   失败
        3   跳过
        4   进行中
    ignored: 忽略
    locked: 锁定, 不再进行重命名等
    deleted: 实际内容已经删除
"""
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from .. import db


class _ScrapingRecords(db.Model):
    """ 刮削记录
    """
    __tablename__ = 'scrapingrecords'

    id = Column(Integer, primary_key=True)
    srcname = Column(String, default='')
    srcpath = Column(String, default='')
    srcsize = Column(BigInteger, default=0)
    status = Column(Integer, default=0)
    ignored = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)

    scrapingname = Column(String, default='', comment='used name for scraping')
    cdnum = Column(Integer, default=0, comment='cd num')
    cnsubtag = Column(Boolean, default=False, comment='cn tag')
    leaktag = Column(Boolean, default=False, comment='leak tag')
    uncensoredtag = Column(Boolean, default=False, comment='uncensored tag')
    hacktag = Column(Boolean, default=False, comment='hack tag')

    # 指定刮削的网站与地址
    # 手动设置
    specifiedsource = Column(String, default='', comment='specified scraping site')
    specifiedurl = Column(String, default='', comment='specified scraping site url')

    linktype = Column(Integer, comment='ln type')
    destname = Column(String, default='', comment='final name')
    destpath = Column(String, default='', comment='final path')
    updatetime = Column(DateTime, default=datetime.datetime.now)
    deadtime = Column(DateTime, default=None, comment='time to delete files')

    def __init__(self, basename, basepath):
        self.srcname = basename
        self.srcpath = basepath

    def serialize(self):
        return {
            'id': self.id,
            'srcname': self.srcname,
            'srcpath': self.srcpath,
            'srcsize': self.srcsize,
            'status': self.status,
            'ignored': self.ignored,
            'locked': self.locked,
            'deleted': self.deleted,
            'scrapingname': self.scrapingname,
            'cdnum': self.cdnum,
            'cnsubtag': self.cnsubtag,
            'leaktag': self.leaktag,
            'uncensoredtag': self.uncensoredtag,
            'hacktag': self.hacktag,
            'specifiedsource': self.specifiedsource,
            'specifiedurl': self.specifiedurl,
            'linktype': self.linktype,
            'destname': self.destname,
            'destpath': self.destpath,
            'updatetime': self.updatetime.strftime("%Y/%m/%d %H:%M:%S") if self.updatetime else '',
            'deadtime': self.deadtime.strftime("%Y/%m/%d %H:%M:%S") if self.deadtime else '',
        }


class _TransRecords(db.Model):
    """ 转移记录
    """
    __tablename__ = 'transrecords'

    id = Column(Integer, primary_key=True)
    srcname = Column(String, default='')
    srcpath = Column(String, default='')
    srcsize = Column(BigInteger, default=0)
    srcfolder = Column(String, default='')

    status = Column(Integer, default=0)
    ignored = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)

    forcedname = Column(String, default='', comment='forced name')
    topfolder = Column(String, default='')
    # 电影类，次级目录;如果是剧集则以season为准
    secondfolder = Column(String, default='')
    isepisode = Column(Boolean, default=False)
    season = Column(Integer, default=-1)
    episode = Column(Integer, default=-1)
    # 链接使用的地址，可能与docker内地址不同
    linkpath = Column(String, default='')
    destpath = Column(String, default='')
    updatetime = Column(DateTime, default=datetime.datetime.utcnow)
    deadtime = Column(DateTime, default=None, comment='time to delete files')

    def __init__(self, basename, basepath):
        self.srcname = basename
        self.srcpath = basepath

    def serialize(self):
        return {
            'id': self.id,
            'srcname': self.srcname,
            'srcpath': self.srcpath,
            'srcsize': self.srcsize,
            'srcfolder': self.srcfolder,
            'status': self.status,
            'ignored': self.ignored,
            'locked': self.locked,
            'deleted': self.deleted,
            'topfolder': self.topfolder,
            'secondfolder': self.secondfolder,
            'isepisode': self.isepisode,
            'season': self.season,
            'episode': self.episode,
            'forcedname': self.forcedname,
            'linkpath': self.linkpath,
            'destpath': self.destpath,
            'updatetime': self.updatetime.strftime("%Y/%m/%d %H:%M:%S") if self.updatetime else '',
            'deadtime': self.deadtime.strftime("%Y/%m/%d %H:%M:%S") if self.deadtime else '',
        }
