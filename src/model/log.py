# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from .. import db


class _ScrapingLog(db.Model):
    __tablename__ = 'info'

    id = Column(Integer, primary_key=True)
    basename = Column(String, default='')
    basepath = Column(String, default='')
    filesize = Column(BigInteger, default=0)
    scrapingname = Column(String, default='', comment='used for scraper')
    status = Column(Integer, default=0)
    newname = Column(String, default='', comment='final name')
    newpath = Column(String, default='', comment='final path')
    updatetime = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, basename, basepath):
        self.basename = basename
        self.basepath = basepath

    def serialize(self):
        return {
            'id': self.id,
            'basename': self.basename,
            'basepath': self.basepath,
            'filesize': self.filesize,
            'scrapingname': self.scrapingname,
            'status': self.status,
            'newname': self.newname,
            'newpath': self.newpath,
            'updatetime': self.updatetime.strftime("%H:%M:%S %m/%d/%Y")
        }



class _TransLog(db.Model):
    __tablename__ = 'transferlog'

    id = Column(Integer, primary_key=True)
    basename = Column(String, default='')
    basepath = Column(String, default='')
    filesize = Column(BigInteger, default=0)
    success = Column(Boolean, default=False)
    softpath = Column(String, default='')
    destpath = Column(String, default='')
    updatetime = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, basename, basepath):
        self.basename = basename
        self.basepath = basepath

    def serialize(self):
        return {
            'id': self.id,
            'basename': self.basename,
            'basepath': self.basepath,
            'filesize': self.filesize,
            'success': self.success,
            'softpath': self.softpath,
            'destpath': self.destpath,
            'updatetime': self.updatetime.strftime("%H:%M:%S %m/%d/%Y")
        }
