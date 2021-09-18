# -*- coding: utf-8 -*-
'''
'''
import os
import pathlib
import stat
import re
import shutil
import requests

from .manager import movie_lists
from .rename import renamebyreg
from ..service.configservice import transConfigService
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService
from ..utils.filehelper import video_type, ext_type, cleanfolderwithoutsuffix,\
     hardlink_force, symlink_force, replace_CJK
from ..utils.log import log


def copysub(src_folder, destfolder, filter):
    """ copy subtitle
    """
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type and filter in item:
            src_file = os.path.join(src_folder, item)
            log.debug("[-] - copy sub  " + src_file)
            dest = shutil.copy(src_file, destfolder)
            # modify permission
            os.chmod(dest, stat.S_IRWXU | stat.S_IRGRP |
                     stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def auto_transfer(real_path: str):
    """ 自动转移
    """
    confs = transConfigService.getConfiglist()
    for conf in confs:
        if real_path.startswith(conf.source_folder):
            log.debug("任务详情: 转移")
            transfer(conf.source_folder, conf.output_folder,
                     conf.linktype, conf.soft_prefix,
                     conf.escape_folder, real_path,
                     False, conf.replace_CJK)
            if conf.refresh_url:
                requests.post(conf.refresh_url)
            break


def ctrl_transfer(src_folder, dest_folder, 
                linktype, prefix, escape_folders,
                renameflag, renameprefix,
                clean_others,
                replace_CJK,
                refresh_url):
    transfer(src_folder, dest_folder, linktype, prefix,
            escape_folders, '', 
            clean_others, replace_CJK,
            renameflag, renameprefix)
    if refresh_url:
        requests.post(refresh_url)


def transfer(src_folder, dest_folder, 
             linktype, prefix,
             escape_folders, top_files='',
             clean_others_tag = True,
             replace_CJK_tag= False,
             renameflag= False, renameprefix='S01E'
             ):
    """ 如果 top_files 有值，则使用 top_files 过滤文件且不清理其他文件
    """

    task = taskService.getTask('transfer')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'transfer')

    try:
        movie_list = []

        if top_files == '':
            movie_list = movie_lists(src_folder, re.split("[,，]", escape_folders))
        else:
            if os.path.exists(top_files):
                clean_others_tag = False
                if os.path.isdir(top_files):
                    movie_list = movie_lists(top_files, re.split("[,，]", escape_folders))
                else:
                    movie_list.append(top_files)

        count = 0
        total = str(len(movie_list))
        taskService.updateTaskTotal(total, 'transfer')
        log.debug('[+]Find  ' + total+'  movies')

        # 硬链接直接使用源目录
        if linktype == 1:
            prefix = src_folder
        # 清理目标目录下的文件：视频 字幕
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        if clean_others_tag:
            dest_list = movie_lists(dest_folder, "")
        else:
            dest_list = []

        for movie_path in movie_list:
            count += 1
            taskService.updateTaskFinished(count, 'transfer')
            log.debug('[!] - ' + str(count) + '/' + total + ' -')
            log.debug("[+] start check [{}] ".format(movie_path))
            movie_info = transrecordService.queryByPath(movie_path)
            if not movie_info:
                movie_info = transrecordService.add(movie_path)

            (filefolder, name) = os.path.split(movie_path)
            midfolder = str(filefolder).replace(src_folder, '').lstrip("\\").lstrip("/")
            # 链接的源地址
            link_path = os.path.join(prefix, midfolder, name)
            # 处理 midfolder 内特殊内容
            # CMCT组视频文件命名比文件夹命名更好
            if 'CMCT' in midfolder and 'CMCT' in name:
                cmovies = movie_lists(filefolder, re.split("[,，]", escape_folders))
                if len(cmovies) == 1:
                    # 只针对单一视频，合集容易出错
                    (sname, ext) = os.path.splitext(name)
                    pdir = os.path.basename(filefolder)
                    midfolder = midfolder.replace(pdir, sname)
                    log.debug("[-] handling midfolder [{}] ".format(midfolder))
            # 替换中文
            if replace_CJK_tag:
                tempmid = midfolder
                tempmid = replace_CJK(tempmid)
                tempmid = re.sub(r'(\W)\1+', r'\1', tempmid).strip('!?@#$.:：【[(（）)]】')
                if len(tempmid) > 8:
                    log.debug("[-] replace CJK [{}] ".format(tempmid))
                    midfolder = tempmid

            # 目的地址
            flag_done = False
            newpath = os.path.join(dest_folder, midfolder, name)
            # https://stackoverflow.com/questions/41941401/how-to-find-out-if-a-folder-is-a-hard-link-and-get-its-real-path
            if os.path.exists(newpath) and os.path.samefile(link_path, newpath):
                flag_done = True
                log.debug("[!] same file already exists")
            elif pathlib.Path(newpath).is_symlink() and os.readlink(newpath) == link_path :
                flag_done = True
                log.debug("[!] link file already exists")
            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)

            if not flag_done:
                log.debug("[-] create link from [{}] to [{}]".format(link_path, newpath))
                if linktype == 0:
                    symlink_force(link_path, newpath)
                else:
                    hardlink_force(link_path, newpath)
            basename = os.path.splitext(name)[0]
            copysub(filefolder, newfolder, basename)

            if newpath in dest_list:
                dest_list.remove(newpath)

            log.info("[-] transfered [{}]".format(newpath))
            transrecordService.update(movie_path, link_path, newpath)

        # 与源内容无匹配
        for torm in dest_list:
            log.info("[!] clean extra file: [{}]".format(torm))
            os.remove(torm)

        cleanfolderwithoutsuffix(dest_folder, video_type)
        # 重命名
        if renameflag:
            reg = '[\[第 ][0-9.svidevoa\(\)]*[\]話话集 ]'
            reg2 = "\.e[0-9videvoa\(\)]{1,}[.]"
            renamebyreg(dest_folder, reg, reg2, renameprefix, False)

        log.info("transfer finished")
    except Exception as e:
        log.error(e)

    taskService.updateTaskStatus(1, 'transfer')

    return True
