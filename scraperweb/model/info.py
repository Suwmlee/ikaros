# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .. import db


class _Info(db.Model):
    __tablename__ = 'info'

    id = Column(Integer, primary_key=True)
    basename = Column(String, default='')
    basepath = Column(String, default='')
    scrapername = Column(String, default='', comment='used for scraper')
    success = Column(Boolean, default=False)
    newname = Column(String, default='', comment='final name')
    updatetime = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, basename, basepath):
        self.basename = basename
        self.basepath = basepath
