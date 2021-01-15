# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from .. import db


class _Task(db.Model):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='task')
    status = Column(Integer, default=0)

    def __init__(self, name):
        self.name = name
