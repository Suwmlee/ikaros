# -*- coding: utf-8 -*-
''' task
'''
from ..model.task import _Task, _AutoTask
from .. import db


class TaskService():

    def getTask(self, taskname) -> _Task:
        task = _Task.query.filter_by(name=taskname).first()
        if not task:
            task = _Task(taskname)
            db.session.add(task)
            db.session.commit()
        return task

    def haveRunningTask(self):
        ntask = _Task.query.filter_by(status=2).first()
        if ntask:
            return True
        return False

    def updateTaskStatus(self, task: _Task, status):
        """ status
            0: wait
            1: finished
            2: runing
        """
        if task.status != status:
            task.status = status
            db.session.commit()

    def updateTaskTotal(self, task: _Task, num):
        """ Update total num
        """
        if task.total != num:
            task.total = num
            db.session.commit()

    def updateTaskFinished(self, task: _Task, num):
        """ Update finished num
        """
        if task.finished != num:
            task.finished = num
            db.session.commit()


class AutoTaskService():

    def init(self, path):
        task = _AutoTask(path)
        db.session.add(task)
        db.session.commit()
        return task

    def reset(self):
        """ 重置
        """
        tasks = _AutoTask.query.filter_by(status=1).all()
        if tasks:
            for t in tasks:
                t.status = 0
            self.commit()

    def getTasks(self):
        return _AutoTask.query.all()

    def getFirst(self):
        return _AutoTask.query.first()

    def getRunning(self):
        return _AutoTask.query.filter_by(status=1).first()

    def getPath(self, path):
        return _AutoTask.query.filter_by(path=path).first()

    def commit(self):
        db.session.commit()

    def deleteTask(self, cid):
        task = _AutoTask.query.filter_by(id=cid).first()
        if task:
            db.session.delete(task)
            db.session.commit()


taskService = TaskService()
autoTaskService = AutoTaskService()
