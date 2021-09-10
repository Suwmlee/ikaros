# -*- coding: utf-8 -*-
'''
'''
import os
import time
import requests

from src.utils.log import log
from ..service.configservice import transConfigService, autoConfigService
from ..service.taskservice import autoTaskService, taskService
from .manager import start_all, start_single
from .transfer import transfer


def start(client_path: str):
    """
    """
    task = autoTaskService.getPath(client_path)
    if task:
        log.info("自动任务: 已经存在任务")
        return 200
    else:
        log.info("自动任务: 加入队列[{}]".format(client_path))
        task = autoTaskService.init(client_path)

    runningTask = autoTaskService.getRunning()
    if runningTask:
        log.info("自动任务: 正在执行其他任务")
    else:
        task_loop()


def task_loop():
    """ 任务循环队列
    """
    running = True
    while running:
        runningTask = autoTaskService.getRunning()
        if runningTask:
            log.info("任务循环队列: 正在执行其他任务")
            break

        task = autoTaskService.getFirst()
        if task:
            log.info("任务循环队列: 开始[{}]".format(task.path))
            task.status = 1
            autoTaskService.commit()
            try:
                # 在已经有任务要进行情况下
                # 其他任务会加入队列，当前任务等待手动任务完成
                while taskService.haveRunningTask():
                    log.info("任务循环队列: 等待手动任务结束")
                    time.sleep(5)

                run_task(task.path)
            except Exception as e:
                log.error(e)
            log.info("任务循环队列: 完成[{}]".format(task.path))
            autoTaskService.deleteTask(task.id)
        else:
            log.info("任务循环队列: 无新任务")
            running = False


def run_task(client_path: str):
    # 1. convert path to real path for flask
    conf = autoConfigService.getSetting()
    real_path = str(client_path).replace(conf.original, conf.prefixed)
    if not os.path.exists(real_path):
        return
    log.info("任务详情: 实际路径[{}]".format(real_path))
    # 2. select scrape or transfer
    scrapingFolders = conf.scrapingfolders.split(';')
    transferFolders = conf.transferfolders.split(';')
    flag_scraping = False
    flag_transfer = False
    for sc in scrapingFolders:
        if real_path.startswith(sc):
            flag_scraping = True
            break
    for sc in transferFolders:
        if real_path.startswith(sc):
            flag_transfer = True
            break
    # 3. run
    if flag_scraping:
        log.info("任务详情: JAV")
        if os.path.isdir(real_path):
            start_all(real_path)
        else:
            start_single(real_path)
    if flag_transfer:
        confs = transConfigService.getConfiglist()
        for conf in confs:
            if real_path.startswith(conf.source_folder):
                log.info("任务详情: 转移")
                transfer(conf.source_folder, conf.output_folder, conf.linktype,
                         conf.soft_prefix, conf.escape_folder, False, '', False, real_path)
                if conf.refresh_url:
                    requests.post(conf.refresh_url)
                break


def clean():
    """ clean all task
    """
    tasks = autoTaskService.getTasks()
    for single in tasks:
        autoTaskService.deleteTask(single.id)
