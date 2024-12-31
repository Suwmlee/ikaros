# -*- coding: utf-8 -*-

import logging
import os
from logging import Logger
from flask import current_app

from .mediaserver import refreshMediaServer
from ..utils.filehelper import checkFolderhasMedia
from ..downloader.transmission import Transmission
from ..bizlogic.manager import startScrapingAll
from ..bizlogic.transfer import ctrlTransfer
from ..service.configservice import scrapingConfService, transConfigService
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
    if scheduler:
        with scheduler.app.app_context():
            cleanRecords(delete)
    else:
        cleanRecords(delete)

def cleanRecords(delete=True):
    if delete:
        scrapingrecordService.cleanUnavailable()
        transrecordService.cleanUnavailable()
    else:
        localconfig = localConfService.getConfig()
        if localconfig.task_clean:
            logger().debug('[-] cleanRecords: start!')
            srecords = scrapingrecordService.deadtimetoMissingrecord()
            trecords = transrecordService.deadtimetoMissingrecord()
            records = list(set(srecords + trecords))
            cleanTorrents(records, localconfig)
            logger().debug('[-] cleanRecords: done!')


def cleanTorrents(records, conf):
    """ 删除关联的torrent
    """
    if not records:
        return
    try:
        trurl = conf.tr_url
        trusername = conf.tr_username
        trpassword = conf.tr_passwd
        trfolder = conf.tr_prefix.split(':')[0]
        prefixed = conf.tr_prefix.split(':')[1]

        if not os.path.exists(prefixed):
            logger().info(f"[-] cleanRecords: Transmission mapped folder does't exist {trfolder} : {prefixed}")
            return
        trs = Transmission(trurl, trusername, trpassword)
        trs.login()
        for path in records:
            logger().debug(f'[-] cleanRecords: check {path}')
            torrents = trs.searchByPath(path)
            for torrent in torrents:
                logger().debug(f'[-] cleanRecords: find torrent {torrent.name}')
                downfolder = os.path.join(torrent.fields['downloadDir'], torrent.name)
                fixedfolder = downfolder.replace(trfolder, prefixed, 1)
                if checkFolderhasMedia(fixedfolder):
                    continue
                trs.removeTorrent(torrent.id, True)
                logger().info(f'[-] cleanRecords: remove torrent {torrent.id} : {torrent.name}')
    except Exception as e:
        logger().error("[-] cleanRecords: You may not have set the transmission or an exception may have occurred.")
        logger().error(e)


def checkDirectoriesTask(scheduler=None):
    """
    无其他任务时,才执行
    增加检测 转移/刮削 文件夹顶层目录内容 计划任务
    间隔10分钟检测是否有新增内容,不需要下载器脚本
    """    
    if scheduler:
        with scheduler.app.app_context():
            autoWatchDirectories()
    else:
        autoWatchDirectories()

def autoWatchDirectories():
    if taskService.haveRunningTask():
        return
    logger().debug('[!] watch Directories')
    logger().debug('watch scraping folder')
    scraping_configs = scrapingConfService.getConfiglist()
    for conf in scraping_configs:
        if conf.auto_watch:
            try:
                logger().debug(f"watch {conf.scraping_folder}")
                startScrapingAll(conf.id)
            except Exception as ex:
                logger().error(ex)
    logger().debug('watch transfer folder')
    transfer_configs = transConfigService.getConfiglist()
    for conf in transfer_configs:
        if conf.auto_watch:
            try:
                logger().debug(f"watch {conf.source_folder}")
                ctrlTransfer(
                    conf.source_folder,
                    conf.output_folder,
                    conf.linktype,
                    conf.soft_prefix,
                    conf.escape_folder,
                    "",
                    conf.fix_series,
                    conf.clean_others,
                    conf.replace_CJK,
                    conf.refresh_url,
                    conf.is_sym_relative_path,
                )
            except Exception as ex:
                logger().error(ex)

def initScheduler():
    """ 初始化
    """
    schedulerService.addJob('cleanRecords', cleanRecordsTask, args=[False, schedulerService.scheduler], seconds=3600)
    schedulerService.addJob('checkDirectories', checkDirectoriesTask, args=[schedulerService.scheduler], seconds=900)


def logger(scheduler=None) -> Logger: 
    if scheduler:
        return scheduler.app.logger
    elif current_app:
        return current_app.logger
    else:
        return logging.getLogger('src')
