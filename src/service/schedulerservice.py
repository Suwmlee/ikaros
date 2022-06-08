# -*- coding: utf-8 -*-
"""
    调度服务
"""
from flask_apscheduler import APScheduler


class SchedulerService():
    """
    """

    def init(self, app):
        self.scheduler = APScheduler()
        self.scheduler.init_app(app)

    def addJob(self, id:str, func, args, seconds:int):
        ''' 增加`interval`类型任务
        '''
        self.scheduler.add_job(id=id, func=func, args=args, trigger='interval', seconds=seconds, timezone="Asia/Shanghai")

    def start(self):
        self.scheduler.start()

schedulerService = SchedulerService()
