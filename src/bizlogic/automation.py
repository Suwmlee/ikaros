# -*- coding: utf-8 -*-
'''
'''
import os
import time
from lxml import etree
from flask import current_app

from scrapinglib import search
from scrapinglib.utils import getTreeElement
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import autoConfigService, transConfigService, scrapingConfService
from ..service.taskservice import autoTaskService, taskService
from ..service.schedulerservice import schedulerService
from .manager import startScrapingAll, startScrapingSingle
from .transfer import autoTransfer
from ..notifications import notificationService


def start(clientPath: str):
    """
    """
    task = autoTaskService.getPath(clientPath)
    if task:
        current_app.logger.info("AutoTask: already exists")
        return 200
    else:
        current_app.logger.info("AutoTask: join TaskQueue [{}]".format(clientPath))
        task = autoTaskService.init(clientPath)

    runningTask = autoTaskService.getRunning()
    if runningTask:
        current_app.logger.debug("AutoTask: working on other tasks")
    else:
        checkTaskQueue()


def checkTaskQueue():
    """ 检查任务队列
    """
    running = True
    while running:
        runningTask = autoTaskService.getRunning()
        if runningTask:
            current_app.logger.debug("TaskQueue: working on other tasks")
            break

        task = autoTaskService.getFirst()
        if task:
            current_app.logger.info("TaskQueue: start [{}]".format(task.path))
            task.status = 1
            autoTaskService.commit()
            try:
                # 在已经有任务要进行情况下
                # 其他任务会加入队列，当前任务等待手动任务完成
                while taskService.haveRunningTask():
                    current_app.logger.debug("TaskQueue: waiting for manual tasks to complete")
                    time.sleep(5)

                runTask(task.path)
            except Exception as e:
                current_app.logger.error(e)
                notificationService.sendtext("托管任务:[{}], 异常:{}".format(task.path, str(e)))
            current_app.logger.info("TaskQueue: finished [{}]".format(task.path))
            autoTaskService.deleteTask(task.id)
        else:
            current_app.logger.info("TaskQueue: found 0 task.")
            running = False


def runTask(client_path: str):
    # 1. convert path to real path for flask
    conf = autoConfigService.getConfig()
    realPath = client_path.replace(conf.original, conf.prefixed)
    if not os.path.exists(realPath):
        current_app.logger.debug("AutoTask details: not exists [{}]".format(realPath))
        return
    current_app.logger.debug("AutoTask details: real path [{}]".format(realPath))
    # 2. select scrape or transfer
    flag_scraping = False
    scrapingConfId = 0
    flag_transfer = False
    transConfigId = 0
    if conf.scrapingconfs:
        scrapingIds = conf.scrapingconfs.split(';')
        if scrapingIds:
            for sid in scrapingIds:
                sconfig = scrapingConfService.getConfig(sid)
                if sconfig and realPath.startswith(sconfig.scraping_folder):
                    flag_scraping = True
                    scrapingConfId = sid
                    break
    else:
        current_app.logger.error("AutoTask details: Not configured!")
    if conf.transferconfs:
        transferIds = conf.transferconfs.split(';')
        if transferIds:
            for tid in transferIds:
                tconfig = transConfigService.getConfigById(tid)
                if tconfig and realPath.startswith(tconfig.source_folder):
                    flag_transfer = True
                    transConfigId = tid
                    break
    else:
        current_app.logger.error("AutoTask details: Not configured!")
    # 3. run
    status = 99
    if flag_scraping:
        current_app.logger.debug("AutoTask details: JAV")
        if os.path.isdir(realPath):
            status = startScrapingAll(scrapingConfId, realPath)
        else:
            status = startScrapingSingle(scrapingConfId, realPath)
        if status == 1 or status == 2:
            records = scrapingrecordService.queryLatest(realPath)
            for record in records:
                # limit = datetime.datetime.now() - datetime.timedelta(minutes=10)
                if record and record.status == 1:
                    sendScrapingMessage(record.srcpath, record.destpath)
            return
        notificationService.sendtext("托管任务:[{}], 刮削异常,详情请查看日志".format(realPath))
    elif flag_transfer:
        current_app.logger.debug("AutoTask details: Transfer")
        status = autoTransfer(transConfigId, realPath)
        if status == 1 or status == 2:
            records = transrecordService.queryLatest(realPath)
            for record in records:
                if record:
                    schedulerService.addJob('autoMessageJob', sendTransferMessage, 
                                    args=[record.srcpath, record.destpath, schedulerService.scheduler], seconds=15)
                    return
        notificationService.sendtext("托管任务:[{}], 转移异常,详情请查看日志".format(realPath))
    else:
        current_app.logger.error("AutoTask details: no matched directory")


def clean():
    """ clean all task
    """
    tasks = autoTaskService.getTasks()
    for single in tasks:
        autoTaskService.deleteTask(single.id)


def sendScrapingMessage(srcpath, dstpath):
    """
    组织发送刮削消息
    """
    headname, ext = os.path.splitext(dstpath)
    nfofile = headname + '.nfo'
    picfile = headname + '-fanart.jpg'
    if os.path.exists(nfofile):
        xmltree = etree.parse(nfofile)
        title = getTreeElement(xmltree, '//title/text()')
        caption = '_更新:_ \n `' + title + '` \n_来源:_ `' + srcpath + '`'
        if notificationService.isTgEnabled():
            if os.path.exists(picfile):
                notificationService.sendTgphoto(caption, picfile)
            else:
                notificationService.sendTgMarkdown(caption)
        if notificationService.isWeEnabled():
            notificationService.sendWeMarkdown(caption)
    else:
        notificationService.sendtext("托管任务:[{}], 刮削完成,已推送媒体库".format(srcpath))


def sendTransferMessage(srcpath, dstpath, scheduler=None):
    """
    组织发送转移消息
    """
    if scheduler:
        scheduler.remove_job(id='autoMessageJob')
    headname, ext = os.path.splitext(dstpath)
    nfofile = headname + '.nfo'
    if os.path.exists(nfofile):
        infopath = dstpath
        xmltree = etree.parse(nfofile)
        title = getTreeElement(xmltree, '//title/text()')
        showtitle = getTreeElement(xmltree, '//showtitle/text()')
        year = getTreeElement(xmltree, '//year/text()')
        imdbid = getTreeElement(xmltree, '//movie/imdbid/text() | //episodedetails/imdbid/text()')
        tmdbid = getTreeElement(xmltree, '//movie/tmdbid/text() | //episodedetails/tmdbid/text()')
        episode = getTreeElement(xmltree, '//episode/text()')
        season = getTreeElement(xmltree, '//season/text()')
        if len(getTreeElement(xmltree, '//episodedetails')):
            cufolder = os.path.dirname(dstpath)
            tvnfopath = os.path.join(cufolder, 'tvshow.nfo')
            if not os.path.exists(tvnfopath):
                tvnfopath = os.path.join(os.path.dirname(cufolder), 'tvshow.nfo')
            if os.path.exists(tvnfopath):
                infopath = tvnfopath
                tvtree = etree.parse(tvnfopath)
                if imdbid == '':
                    imdbid = getTreeElement(tvtree, '//tvshow/imdb_id/text()')
                if tmdbid == '':
                    tmdbid = getTreeElement(tvtree, '//tvshow/tmdbid/text()')

        if notificationService.isTgEnabled():

            if showtitle != '':
                text = '_更新_ \n*' + showtitle + '* ('+ year +') \n'
            else:
                text = '_更新_ \n*' + title + '* ('+ year +') \n'
            if imdbid != '' or tmdbid != '':
                text += '【 '
                if imdbid: 
                    text += '[IMDB](https://www.imdb.com/title/'+ imdbid +')  '
                if tmdbid:
                    text += '[TMDB](https://www.themoviedb.org/movie/' + tmdbid + '?language=zh-CN) ' 
                text += ' 】\n' 
            text += '_来源:_ `' + srcpath + '`'

            photopath = getPhotoPath(infopath)
            if photopath:
                notificationService.sendTgphoto(text, photopath)
            else:
                notificationService.sendTgMarkdown(text)

        if notificationService.isWeEnabled():
            if tmdbid != '':
                jsondata = search(tmdbid, type='general')
                imageurl = jsondata.get('cover')
                text_title = '更新  ' + title + ' ('+ year +')'
                text_description = '来源: ' + srcpath
                text_url = 'https://www.themoviedb.org/movie/' + tmdbid + '?language=zh-CN'
                notificationService.sendWeNews(text_title, text_description, imageurl, text_url)
            else:
                notificationService.sendtext("托管:[{}], 转移完成,媒体库未自动识别,请手动识别".format(srcpath))
    else:
        # TODO 不存在文件,自己解析？
        notificationService.sendtext("托管:[{}], 转移完成,媒体库未自动识别,请手动识别".format(srcpath))

def getPhotoPath(filepath):
    headname, ext = os.path.splitext(filepath)
    photopath = headname + '-poster.jpg'
    if os.path.exists(photopath):
        return photopath
    else:
        cfolder = os.path.dirname(filepath)
        photopath = os.path.join(cfolder, 'poster.jpg')
        if os.path.exists(photopath):
            return photopath
        else:
            photopath = headname + '-thumb.jpg'
            if os.path.exists(photopath):
                return photopath
    return ''
