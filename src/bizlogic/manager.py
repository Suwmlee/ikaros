# -*- coding: utf-8 -*-
'''
'''
import os
import re

from ..service.configservice import scrapingConfService, _ScrapingConfigs
from ..service.recordservice import scrapingrecordService
from ..service.taskservice import taskService
from .scraper import core_main, moveFailedFolder
from ..utils.log import log
from ..utils.number_parser import get_number
from ..utils.filehelper import cleanscrapingfile, video_type, CleanFolder, cleanfolderbyfilter


def movie_lists(root, escape_folder):
    """ collect movies
    
    won't check link path
    """
    if os.path.basename(root) in escape_folder:
        return []
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1].lower() in video_type:
            total.append(f)
    return total


def create_data_and_move(file_path: str, conf: _ScrapingConfigs):
    """ start scrape single file
    """
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    n_number = get_number(file_path)
    scrapingtag_cnsub = False
    scrapingtag_cdnum = 0
    try:
        movie_info = scrapingrecordService.queryByPath(file_path)
        # 查看单个文件刮削状态
        if not movie_info or (movie_info.status != 1 and movie_info.status != 3):
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
                        cleanscrapingfile(folder, filter)
                    else:
                        cleanfolderbyfilter(folder, filter)
            # 查询是否有额外设置
            if movie_info.scrapingname != '':
                n_number = movie_info.scrapingname
            if movie_info.cnsubtag:
                scrapingtag_cnsub = True
            if movie_info.cdnum:
                scrapingtag_cdnum = movie_info.cdnum
            log.info("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            (flag, new_path) = core_main(file_path, n_number, scrapingtag_cnsub, scrapingtag_cdnum, conf)
            movie_info = scrapingrecordService.update(file_path, n_number, new_path, flag, conf.link_type)
        else:
            # use cleandb function checking record
            log.info("[!]Already done: [{}]".format(file_path))
    except Exception as err:
        log.error("[!] ERROR: [{}] ".format(file_path))
        log.error(err)
        moveFailedFolder(file_path)
    log.info("[*]======================================================")


def start_all(folder=''):
    """ 启动入口
    """

    task = taskService.getTask('scrape')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'scrape')

    conf = scrapingConfService.getSetting()
    CleanFolder(conf.failed_folder)

    if folder == '':
        folder = conf.scraping_folder
    movie_list = movie_lists(conf.scraping_folder, re.split("[,，]", conf.escape_folders))

    count = 0
    total = str(len(movie_list))
    taskService.updateTaskFinished(0, 'scrape')
    taskService.updateTaskTotal(total, 'scrape')
    log.info('[+]Find  ' + total+'  movies')

    for movie_path in movie_list:
        taskService.updateTaskFinished(count, 'scrape')
        percentage = str(count / int(total) * 100)[:4] + '%'
        log.info('[!] - ' + percentage + ' [' + str(count) + '/' + total + '] -')
        create_data_and_move(movie_path, conf)
        count = count + 1

    log.info("[+]All finished!!!")

    taskService.updateTaskStatus(1, 'scrape')


def start_single(movie_path: str):
    """ single movie
    """
    task = taskService.getTask('scrape')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'scrape')

    log.info("[+]Single start!!!")
    if os.path.exists(movie_path):
        conf = scrapingConfService.getSetting()
        create_data_and_move(movie_path, conf)

    log.info("[+]Single finished!!!")

    taskService.updateTaskStatus(1, 'scrape')
