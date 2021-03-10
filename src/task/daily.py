# -*- coding: utf-8 -*-
'''
    每日计划任务


'''

from flask_apscheduler import APScheduler
from ..bizlogic import manager, scraper, transfer

class DailyTask(object):
    """
        每日任务
    """

    def __init__(self, app):
        self.scheduler = APScheduler()
        self.flaskapp = app

    def start(self):
        ''' 启动任务
        '''

        def dailyjob():
            try:
                print("start task")
            except:
                print("start task")

        # 计划任务部分
        self.scheduler.init_app(self.flaskapp)
        self.scheduler.add_job(id='daily_job', func=dailyjob,
                               trigger='cron', day_of_week='*', hour=0, minute=0, second=1)

        self.scheduler.start()
