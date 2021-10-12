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
     hardlink_force, symlink_force, replace_CJK, cleanbyNameSuffix, cleanExtraMedia
from ..utils.log import log


class FileInfo():

    realpath = ''
    realfolder = ''
    realname = ''
    folders = []

    midfolder = ''
    topfolder = ''
    secondfolder = ''
    name = ''
    ext = ''

    finalpath = ''
    finalfolder = ''

    def __init__(self, filepath):
        self.realpath = filepath
        (filefolder, filename) = os.path.split(filepath)
        self.realfolder = filefolder
        self.realname = filename
        (name, ext) = os.path.splitext(filename)
        self.name = name
        self.ext = ext

    def updatemidfolder(self, mid):
        self.midfolder = mid
        folders =  os.path.normpath(mid).split(os.path.sep)
        self.folders = folders
        self.topfolder = folders[0]
        if len(folders) > 1:
            self.secondfolder = folders[1]

    def fixmidfolder(self):
        temp = self.folders
        temp[0] = self.topfolder
        if self.secondfolder != '':
            if len(temp) > 1:
                temp[1] = self.secondfolder
            else:
                temp.append(self.secondfolder)
        return os.path.join(*temp)
    
    def updatefinalpath(self, path):
        self.finalpath = path
        (newfolder, tname) = os.path.split(path)
        self.finalfolder = newfolder


def copysub(src_folder, destfolder, filter):
    """ copy subtitle
    """
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type and path.startswith(filter):
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

        todoFiles = []
        for movie_path in movie_list:
            fi = FileInfo(movie_path)
            midfolder = fi.realfolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            fi.updatemidfolder(midfolder)
            todoFiles.append(fi)

        for currentfile in todoFiles:
            count += 1
            taskService.updateTaskFinished(count, 'transfer')
            log.debug('[!] - ' + str(count) + '/' + total + ' -')
            log.debug("[+] start check [{}] ".format(currentfile.realpath))
            transrecordService.add(currentfile.realpath)

            # 修正后给链接使用的源地址
            link_path = os.path.join(prefix, currentfile.midfolder, currentfile.realname)
            # 处理 midfolder 内特殊内容
            # TODO 给单视频文件创建文件夹

            # CMCT组视频文件命名比文件夹命名更好
            # TODO 可延申过滤剧集，S01 S02，只过滤 topfolder下的文件， seoondfolder = ''
            # 得到剧集后，修改 secondfolder 为季度
            # 与之后的 renameflag 配合 ？？
            if 'CMCT' in currentfile.topfolder:
                matches = [x for x in todoFiles if x.topfolder == currentfile.topfolder]
                if len(matches) > 0:
                    namingfiles = [x for x in matches if 'CMCT' in x.name]
                    if len(namingfiles) == 1:
                        for m in matches:
                            m.topfolder = namingfiles[0].name
                    log.debug("[-] handling midfolder [{}] ".format(midfolder))
            # 替换中文
            if replace_CJK_tag:
                tempmid = currentfile.topfolder
                tempmid = replace_CJK(tempmid)
                tempmid = re.sub(r'(\W)\1+', r'\1', tempmid).strip(' !?@#$.:：【[(（）)]】')
                if len(tempmid) > 18:
                    log.debug("[-] replace CJK [{}] ".format(tempmid))
                    currentfile.topfolder = tempmid
            # 检测是否是特殊的导评/花絮内容
            # TODO 更多关于花絮的规则
            if currentfile.name == "导演访谈":
                if currentfile.secondfolder == '' and currentfile.topfolder != '.':
                    currentfile.secondfolder = "extras"

            flag_done = False
            if currentfile.topfolder == '.':
                newpath = os.path.join(dest_folder, currentfile.name + currentfile.ext)
            else:
                newpath = os.path.join(dest_folder, currentfile.fixmidfolder(), currentfile.name + currentfile.ext)
            currentfile.updatefinalpath(newpath)
            newfolder = currentfile.finalfolder
            # https://stackoverflow.com/questions/41941401/how-to-find-out-if-a-folder-is-a-hard-link-and-get-its-real-path
            if os.path.exists(newpath) and os.path.samefile(link_path, newpath):
                flag_done = True
                log.debug("[!] same file already exists")
            elif pathlib.Path(newpath).is_symlink() and os.readlink(newpath) == link_path :
                flag_done = True
                log.debug("[!] link file already exists")
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            if not flag_done:
                log.debug("[-] create link from [{}] to [{}]".format(link_path, newpath))
                if linktype == 0:
                    symlink_force(link_path, newpath)
                else:
                    hardlink_force(link_path, newpath)

            # 使用最终的文件名
            cleanbyNameSuffix(currentfile.finalfolder, currentfile.name, ext_type)
            # TODO 原始的文件名，如果更改文件名，则需要更新此方法
            nname = os.path.splitext(currentfile.realname)[0]
            copysub(currentfile.realfolder, currentfile.finalfolder, nname)

            if newpath in dest_list:
                dest_list.remove(newpath)

            log.info("[-] transfered [{}]".format(newpath))
            transrecordService.update(currentfile.realpath, link_path, newpath)

        if clean_others_tag:
            for torm in dest_list:
                log.info("[!] clean extra file: [{}]".format(torm))
                os.remove(torm)
            cleanExtraMedia(dest_folder)
            cleanfolderwithoutsuffix(dest_folder, video_type)

        # TODO 剧集重命名
        # 目前只针对顶层目录，适用范围较低
        if renameflag:
            renamebyreg(dest_folder, '', renameprefix, False)

        log.info("transfer finished")
    except Exception as e:
        log.error(e)

    taskService.updateTaskStatus(1, 'transfer')

    return True
