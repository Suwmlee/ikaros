# -*- coding: utf-8 -*-
'''
'''
import os
import re

from ..service.configservice import scrapingConfService
from ..service.recordservice import scrapingrecordService
from ..service.taskservice import taskService
from .scraper import core_main
from ..utils.wlogger import wlogger
from ..utils.number_parser import get_number
from ..utils.filehelper import video_type, CreatFolder


def movie_lists(root, escape_folder):
    """ collect movies
    """
    for folder in escape_folder:
        if folder in root and folder != '':
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


def CEF(path):
    """ clean empty folder
    """
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            wlogger.info('[+]Deleting empty folder', path + '/' + file)
    except:
        pass


def create_data_and_move(file_path: str, conf):
    """ start scrape single file
    """
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    debug = conf.debug_info
    n_number = get_number(debug, file_path)
    scrapingtag_cnsub = False
    try:
        movie_info = scrapingrecordService.queryByPath(file_path)
        if not movie_info or movie_info.status != 1:
            movie_info = scrapingrecordService.add(file_path)
            if movie_info.scrapingname != '':
                n_number = movie_info.scrapingname
            if movie_info.cnsubtag:
                scrapingtag_cnsub = True
            wlogger.info("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            (flag, new_path) = core_main(file_path, n_number, scrapingtag_cnsub, conf)
            movie_info = scrapingrecordService.update(file_path, n_number, new_path, flag)
        else:
            wlogger.info("[!]Already done: [{}]".format(file_path))
        wlogger.info("[*]======================================================")
    except Exception as err:
        wlogger.error("[-] [{}] ERROR:".format(file_path))
        wlogger.error(err)


def start():
    """ 启动入口
    """

    task = taskService.getTask('scrape')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'scrape')

    conf = scrapingConfService.getSetting()
    CreatFolder(conf.failed_folder)

    movie_list = movie_lists(conf.scraping_folder, re.split("[,，]", conf.escape_folders))

    count = 0
    count_all = str(len(movie_list))
    wlogger.info('[+]Find  ' + count_all+'  movies')
    if conf.debug_info:
        wlogger.info('[+]'+' DEBUG MODE ON '.center(54, '-'))
    if conf.soft_link:
        wlogger.info('[!] --- Soft link mode is ENABLE! ----')
    for movie_path in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        wlogger.info('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        create_data_and_move(movie_path, conf)

    CEF(conf.success_folder)
    CEF(conf.failed_folder)
    wlogger.info("[+]All finished!!!")
    wlogger.info("[+]All finished!!!")

    taskService.updateTaskStatus(1, 'scrape')
