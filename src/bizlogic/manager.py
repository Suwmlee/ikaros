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
from ..utils.ADC_function import is_link
from ..utils.number_parser import get_number
from ..utils.filehelper import video_type, CreatFolder, cleanfolderbyfilter


def movie_lists(root, escape_folder):
    """ collect movies
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
            absf = os.path.abspath(f)
            if not is_link(absf):
                total.append(absf)
    return total


def rm_empty_folder(path):
    """ clean empty folder
    """
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
    except:
        return
    for file in files:
        try:
            os.rmdir(path + '/' + file)  # 删除这个空文件夹
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
        # 查看单个文件刮削状态
        if not movie_info or (movie_info.status != 1 and movie_info.status != 3):
            movie_info = scrapingrecordService.add(file_path)
            # 查询是否已经存在刮削目录 & 不能在同一目录下
            if movie_info.destpath != '':
                basefolder = os.path.dirname(movie_info.srcpath)
                folder = os.path.dirname(movie_info.destpath)
                if os.path.exists(folder) and basefolder != folder:
                    name = os.path.basename(movie_info.destpath)
                    filter  = os.path.splitext(name)[0]
                    cleanfolderbyfilter(folder, filter)
            # 查询是否有额外设置
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
    total = str(len(movie_list))
    taskService.updateTaskTotal(total, 'scrape')
    wlogger.info('[+]Find  ' + total+'  movies')

    for movie_path in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        taskService.updateTaskFinished(count, 'scrape')
        percentage = str(count / int(total) * 100)[:4] + '%'
        wlogger.info('[!] - ' + percentage + ' [' + str(count) + '/' + total + '] -')
        create_data_and_move(movie_path, conf)

    rm_empty_folder(conf.success_folder)
    rm_empty_folder(conf.failed_folder)
    
    wlogger.info("[+]All finished!!!")

    taskService.updateTaskStatus(1, 'scrape')
