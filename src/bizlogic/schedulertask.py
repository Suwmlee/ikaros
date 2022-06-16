# -*- coding: utf-8 -*-


from logging import Logger
from flask import current_app

from ..service.taskservice import taskService
from ..service.schedulerservice import schedulerService
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import localConfService


def cleanRecordsTask(delete=True, scheduler=None):
    """
    TODO 关联下载器
    清除记录任务
    放开emby内删除文件权限,用户在emby内删除文件,ikaros检测到文件不存在
    增加 等待删除 标记，三天后，真正删除文件，种子文件
    """
    if delete:
        scrapingrecordService.cleanUnavailable()
        transrecordService.cleanUnavailable()
    else:
        localconfig = localConfService.getConfig()
        if localconfig.task_clean:
            logger(scheduler).info('cleanRecords')
            scrapingrecordService.deadtimetoMissingrecord()
            transrecordService.deadtimetoMissingrecord()
            logger(scheduler).info('done!')


def checkDirectoriesTask(scheduler=None):
    """
    TODO
    无其他任务时,才执行
    增加检测 转移/刮削 文件夹顶层目录内容 计划任务
    间隔3分钟检测是否有新增内容,不需要下载器脚本
    """
    if taskService.haveRunningTask():
        return
    logger(scheduler).info('checkDirectories')


def initScheduler():
    """ 初始化
    """
    schedulerService.addJob('cleanRecords', cleanRecordsTask, args=[False, schedulerService.scheduler], seconds=300)
    # schedulerService.addJob('checkDirectories', checkDirectoriesTask, args=[schedulerService.scheduler], seconds=180)


def logger(scheduler=None) -> Logger: 
    if scheduler:
        return scheduler.app.logger
    else:
        return current_app.logger

