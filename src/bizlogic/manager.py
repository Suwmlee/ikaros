# -*- coding: utf-8 -*-
'''
'''
import os
import re
import datetime

from ..service.configservice import scrapingConfService, _ScrapingConfigs
from ..service.recordservice import scrapingrecordService
from ..service.taskservice import taskService
from .scraper import core_main, moveFailedFolder
from .mediaserver import refreshMediaServer
from flask import current_app
from ..utils.number_parser import FileNumInfo
from ..utils.filehelper import cleanScrapingfile, video_type, cleanFolder, cleanFolderbyFilter


def findAllMovies(root, escape_folder):
    """ find all movies
    """
    if os.path.basename(root) in escape_folder:
        return []
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += findAllMovies(f, escape_folder)
        elif os.path.splitext(f)[1].lower() in video_type:
            total.append(f)
    return total


def create_data_and_move(file_path: str, conf: _ScrapingConfigs):
    """ scrape single file
    """
    try:
        movie_info = scrapingrecordService.queryByPath(file_path)
        # 查看单个文件刮削状态
        if not movie_info or (movie_info.status != 1 and movie_info.status != 3 and movie_info.status != 4):
            movie_info = scrapingrecordService.add(file_path)
            # 查询是否已经存在刮削目录 & 不能在同一目录下
            if movie_info.destpath != '':
                basefolder = os.path.dirname(movie_info.srcpath)
                folder = os.path.dirname(movie_info.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(movie_info.destpath)
                    filter = os.path.splitext(name)[0]
                    if movie_info.cdnum and movie_info.cdnum > 0:
                        # 如果是多集，则只清理当前文件
                        cleanScrapingfile(folder, filter)
                    else:
                        cleanFolderbyFilter(folder, filter)
            num_info = FileNumInfo(file_path)
            # 查询是否有额外设置
            if movie_info.scrapingname != '':
                num_info.num = movie_info.scrapingname
            if movie_info.cnsubtag:
                num_info.chs_tag = True
            if movie_info.cdnum:
                num_info.updateCD(movie_info.cdnum)
            current_app.logger.info("[!]Making Data for [{}], the number is [{}]".format(file_path, num_info.num))
            movie_info.status = 4
            movie_info.scrapingname = num_info.num
            movie_info.updatetime = datetime.datetime.now()
            scrapingrecordService.commit()
            (flag, new_path) = core_main(file_path, num_info, conf)
            if flag:
                movie_info.status = 1
                (filefolder, newname) = os.path.split(new_path)
                movie_info.destname = newname
                movie_info.destpath = new_path
                movie_info.linktype = conf.link_type
                movie_info.cnsubtag = num_info.chs_tag
                if num_info.multipart_tag:
                    movie_info.cdnum = num_info.part[3:]
            else:
                movie_info.status = 2
            movie_info.updatetime = datetime.datetime.now()
            scrapingrecordService.commit()
        else:
            # use cleandb function checking record
            current_app.logger.info("[!]Already done: [{}]".format(file_path))
    except Exception as err:
        current_app.logger.error("[!] ERROR: [{}] ".format(file_path))
        current_app.logger.error(err)
        moveFailedFolder(file_path)
    current_app.logger.info("[*]======================================================")


def startScrapingAll(folder=''):
    """ 启动入口
    """

    task = taskService.getTask('scrape')
    if task.status == 2:
        return
    taskService.updateTaskStatus(task, 2)

    conf = scrapingConfService.getSetting()
    cleanFolder(conf.failed_folder)

    if folder == '':
        folder = conf.scraping_folder
    movie_list = findAllMovies(folder, re.split("[,，]", conf.escape_folders))

    count = 0
    total = str(len(movie_list))
    taskService.updateTaskNum(task, total)
    current_app.logger.info("[*]======================================================")
    current_app.logger.info('[+]Find  ' + total+'  movies')

    for movie_path in movie_list:
        task = taskService.getTask('scrape')
        if task.status == 0:
            return
        taskService.updateTaskFinished(task, count)
        percentage = str(count / int(total) * 100)[:4] + '%'
        current_app.logger.debug('[!] - ' + percentage + ' [' + str(count) + '/' + total + '] -')
        create_data_and_move(movie_path, conf)
        count = count + 1

    taskService.updateTaskStatus(task, 1)

    if conf.refresh_url:
        current_app.logger.info("[+]Refresh MediaServer")
        refreshMediaServer(conf.refresh_url)

    current_app.logger.info("[+] All scraping finished!!!")
    current_app.logger.info("[*]======================================================")


def startScrapingSingle(movie_path: str):
    """ single movie
    """
    task = taskService.getTask('scrape')
    if task.status == 2:
        return
    taskService.updateTaskStatus(task, 2)

    current_app.logger.info("[+]Single start!!!")
    if os.path.exists(movie_path) and os.path.isfile(movie_path):
        conf = scrapingConfService.getSetting()
        create_data_and_move(movie_path, conf)

    taskService.updateTaskStatus(task, 1)

    if conf.refresh_url:
        current_app.logger.info("[+]Refresh MediaServer")
        refreshMediaServer(conf.refresh_url)

    current_app.logger.info("[+]Single finished!!!")
