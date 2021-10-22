# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from .. import db


class _ScrapingRecords(db.Model):
    """ 刮削记录
    status  0   未刮削
            1   已刮削
            2   失败
            3   忽略
            4   进行中
    """
    __tablename__ = 'scrapingrecords'

    id = Column(Integer, primary_key=True)
    srcname = Column(String, default='')
    srcpath = Column(String, default='')
    srcsize = Column(BigInteger, default=0)
    status = Column(Integer, default=0)
    
    scrapingname = Column(String, default='', comment='used name for scraping')
    cdnum = Column(Integer, default=0, comment='cd num')
    cnsubtag = Column(Boolean, default=False, comment='cn sub')
    scrapingurl = Column(String, default='', comment='scraping site url')

    linktype = Column(Integer, comment='ln type')
    destname = Column(String, default='', comment='final name')
    destpath = Column(String, default='', comment='final path')
    updatetime = Column(DateTime, default=datetime.datetime.now)

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
            'scrapingname': self.scrapingname,
            'cdnum': self.cdnum,
            'cnsubtag': self.cnsubtag,
            'scrapingurl': self.scrapingurl,
            'linktype': self.linktype,
            'destname': self.destname,
            'destpath': self.destpath,
            'updatetime': self.updatetime.strftime("%H:%M:%S %m/%d/%Y")
        }



class _TransRecords(db.Model):
    """ 转移记录
    status  0   
            1   锁定
            2   忽略
    """
    __tablename__ = 'transrecords'

    id = Column(Integer, primary_key=True)
    srcname = Column(String, default='')
    srcpath = Column(String, default='')
    srcsize = Column(BigInteger, default=0)
    success = Column(Boolean, default=False)
    status = Column(Integer, default=0)

    topfolder = Column(String, default='')
    secondfolder = Column(String, default='')
    isepisode = Column(Boolean, default=False)
    season = Column(Integer, default=-1)
    episode = Column(Integer, default=-1)

    linkpath = Column(String, default='')
    destpath = Column(String, default='')
    updatetime = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, basename, basepath):
        self.srcname = basename
        self.srcpath = basepath

    def serialize(self):
        return {
            'id': self.id,
            'srcname': self.srcname,
            'srcpath': self.srcpath,
            'srcsize': self.srcsize,
            'success': self.success,
            'status':self.status,
            'isepisode':self.isepisode,
            'season':self.season,
            'episode':self.episode,
            'linkpath': self.linkpath,
            'destpath': self.destpath,
            'updatetime': self.updatetime.strftime("%H:%M:%S %m/%d/%Y")
        }
