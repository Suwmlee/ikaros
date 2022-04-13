# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from .. import db


class _Task(db.Model):        
    """ status
        0: wait
        1: finished
        2: runing
    """
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='task')
    cid = Column(Integer, default=0)
    status = Column(Integer, default=0)

    total = Column(Integer, default=0)
    finished = Column(Integer, default=0)

    def __init__(self, name):
        self.name = name


class _AutoTask(db.Model):
    """ 自动任务，成功的任务自动删除
    status  0   未进行
            1   进行中
    """
    __tablename__ = 'autotask'

    id = Column(Integer, primary_key=True)
    path = Column(String, default='', comment="客户端传入路径")
    status = Column(Integer, default=0, comment="状态")

    def __init__(self, path):
        self.path = path

    def serialize(self):
        return {
            'id': self.id,
            'path': self.path,
            'status': self.status,
        }
