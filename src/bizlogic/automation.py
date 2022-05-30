# -*- coding: utf-8 -*-
'''
'''
import os
import time
import xml.etree.ElementTree as ET
from flask import current_app

from ..scrapinglib import search
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import autoConfigService, transConfigService, scrapingConfService
from ..service.taskservice import autoTaskService, taskService
from .manager import startScrapingAll, startScrapingSingle
from .transfer import autoTransfer
from ..notifications import notificationService


def start(clientPath: str):
    """
    """
    task = autoTaskService.getPath(clientPath)
    if task:
        current_app.logger.info("托管任务: 已经存在任务")
        return 200
    else:
        current_app.logger.info("托管任务: 加入队列[{}]".format(clientPath))
        task = autoTaskService.init(clientPath)

    runningTask = autoTaskService.getRunning()
    if runningTask:
        current_app.logger.debug("托管任务: 正在执行其他任务")
    else:
        checkTaskQueue()


def checkTaskQueue():
    """ 任务循环队列
    """
    running = True
    while running:
        runningTask = autoTaskService.getRunning()
        if runningTask:
            current_app.logger.debug("任务循环队列: 正在执行其他任务")
            break

        task = autoTaskService.getFirst()
        if task:
            current_app.logger.info("任务循环队列: 开始[{}]".format(task.path))
            task.status = 1
            autoTaskService.commit()
            try:
                # 在已经有任务要进行情况下
                # 其他任务会加入队列，当前任务等待手动任务完成
                while taskService.haveRunningTask():
                    current_app.logger.debug("任务循环队列: 等待手动任务结束")
                    time.sleep(5)

                runTask(task.path)
            except Exception as e:
                current_app.logger.error(e)
                notificationService.sendtext("托管任务:[{}], 异常:{}".format(task.path,str(e)))
            current_app.logger.info("任务循环队列: 清除任务[{}]".format(task.path))
            autoTaskService.deleteTask(task.id)
        else:
            current_app.logger.info("任务循环队列: 无新任务")
            running = False


def runTask(client_path: str):
    # 1. convert path to real path for flask
    conf = autoConfigService.getConfig()
    realPath = client_path.replace(conf.original, conf.prefixed)
    if not os.path.exists(realPath):
        current_app.logger.debug("任务详情: 不存在路径[{}]".format(realPath))
        return
    current_app.logger.debug("任务详情: 实际路径[{}]".format(realPath))
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
        current_app.logger.error("任务详情: 未配置 自动-刮削配置,请配置后再使用")
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
        current_app.logger.error("任务详情: 未配置 自动-转移配置,请配置后再使用")
    # 3. run
    status = 99
    if flag_scraping:
        current_app.logger.debug("任务详情: JAV")
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
        status = autoTransfer(transConfigId, realPath)
        if status == 1 or status == 2:
            records = transrecordService.queryLatest(realPath)
            for record in records:
                if record:
                    from .. import executor
                    executor.submit(waitTask(record.srcpath, record.destpath))
                    return
        notificationService.sendtext("托管任务:[{}], 转移异常,详情请查看日志".format(realPath))
    else:
        current_app.logger.error("无匹配的目录")


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
        tree = ET.parse(nfofile)
        root = tree.getroot()
        title = root.find('title').text
        caption = '新增影片 \n*标题:* `' + title + '` \n_来源:_ `' + srcpath + '`'
        if notificationService.isTgEnabled():
            if os.path.exists(picfile):
                notificationService.sendTgphoto(caption, picfile)
            else:
                notificationService.sendTgMarkdown(caption)
        if notificationService.isWeEnabled():
            notificationService.sendWeMarkdown(caption)
    else:
        notificationService.sendtext("托管任务:[{}], 刮削完成,已推送媒体库".format(srcpath))


def waitTask(srcpath, dstpath):
    """
    等待 emby 更新完再提取
    """
    time.sleep(15)
    sendTransferMessage(srcpath, dstpath)


def sendTransferMessage(srcpath, dstpath):
    """
    组织发送转移消息
    """
    headname, ext = os.path.splitext(dstpath)
    nfofile = headname + '.nfo'
    if os.path.exists(nfofile):
        tree = ET.parse(nfofile)
        root = tree.getroot()
        title = root.findtext('title')
        year = root.findtext('year')
        imdbid = root.findtext('imdbid')
        tmdbid = root.findtext('tmdbid')
        if notificationService.isTgEnabled() and title and year and tmdbid and imdbid:
            if root.tag == 'episodedetails':
                # tvshow info
                showtitle = root.findtext('showtitle')
                episode = root.findtext('episode')
                season = root.findtext('season')
                text = '新增剧集 \n*' + showtitle + '* ('+ year +') \n'
                text = text + '第 ' + season + ' 季 ' + episode + ' 集 '+ title +' \n'
                text = text + '【 [IMDB](https://www.imdb.com/title/'+ imdbid \
                            +') | [TMDB](https://www.themoviedb.org/movie/' + tmdbid + '?language=zh-CN) 】\n' 
                text = text + '_来源:_ `' + srcpath + '`'
                picfile = headname + '-thumb.jpg'
                if os.path.exists(picfile):
                    notificationService.sendTgphoto(text, picfile)
                else:
                    notificationService.sendTgMarkdown(text)
            else:
                # movie
                picfile = headname + '-poster.jpg'
                if not os.path.exists(picfile):
                    cfolder = os.path.dirname(dstpath)
                    picfile = os.path.join(cfolder, 'poster.jpg')

                text = '新增影片 \n*' + title + '* ('+ year +') \n'
                text = text + '【 [IMDB](https://www.imdb.com/title/'+ imdbid \
                            +') | [TMDB](https://www.themoviedb.org/movie/' + tmdbid + '?language=zh-CN) 】\n' 
                text = text + '_来源:_ `' + srcpath + '`'
                if os.path.exists(picfile):
                    notificationService.sendTgphoto(text, picfile)
                else:
                    notificationService.sendTgMarkdown(text)

        if notificationService.isWeEnabled() and title and year and tmdbid:
            jsondata = search(tmdbid, type='general')
            imageurl = jsondata.get('cover')
            text_title = '新增  ' + title + ' ('+ year +')'
            text_description = '来源: ' + srcpath
            text_url = 'https://www.themoviedb.org/movie/' + tmdbid + '?language=zh-CN'
            notificationService.sendWeNews(text_title, text_description, imageurl, text_url)
    else:
        notificationService.sendtext("托管任务:[{}], 转移完成,推送媒体库异常".format(srcpath))
