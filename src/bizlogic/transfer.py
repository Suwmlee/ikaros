# -*- coding: utf-8 -*-
'''
'''
import os
import pathlib
import stat
import re
import shutil
import requests

from .manager import findAllMovies
from .rename import extractEpNum, matchSeason, matchEpPart
from ..service.configservice import transConfigService
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService
from ..utils.filehelper import replaceRegex, video_type, ext_type, cleanFolderWithoutSuffix,\
     forceHardlink, forceSymlink, replaceCJK, cleanbyNameSuffix, cleanExtraMedia
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

    isepisode = False
    originep = ''
    epnum = ''

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

    def updateMidFolder(self, mid):
        self.midfolder = mid
        folders =  os.path.normpath(mid).split(os.path.sep)
        self.folders = folders
        self.topfolder = folders[0]
        if len(folders) > 1:
            self.secondfolder = folders[1]

    def fixMidFolder(self):
        temp = self.folders
        temp[0] = self.topfolder
        if self.secondfolder != '':
            if len(temp) > 1:
                temp[1] = self.secondfolder
            else:
                temp.append(self.secondfolder)
        return os.path.join(*temp)
    
    def updateFinalPath(self, path):
        self.finalpath = path
        (newfolder, tname) = os.path.split(path)
        self.finalfolder = newfolder

    def parse(self):
        originep = matchEpPart(self.name)
        if originep:
            epresult = extractEpNum(originep)
            if epresult:
                self.isepisode = True
                self.originep = originep
                self.epnum = epresult

    def fixEpName(self, season):
        prefix = "S%02dE" % (season)
        log.debug(self.originep + "   " + self.epnum)
        if self.originep[0] == '.':
            renum = "." + prefix + self.epnum + "."
        elif self.originep[0] == '[':
            renum = "[" + prefix + self.epnum + "]"
        else:
            renum = " " + prefix + self.epnum + " "
        log.debug("替换内容：" + renum)
        newname = self.name.replace(self.originep, renum)
        self.name = newname
        log.info("替换后:   {}".format(newname))


def copySubs(srcfolder, destfolder, basename, newname):
    """ copy subtitle
    """
    dirs = os.listdir(srcfolder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type and path.startswith(basename):
            src_file = os.path.join(srcfolder, item)
            newpath = path.replace(basename, newname)
            log.debug("[-] - copy sub  " + src_file)
            newfile = os.path.join(destfolder, newpath + ext)
            shutil.copyfile(src_file, newfile)
            # modify permission
            os.chmod(newfile, stat.S_IRWXU | stat.S_IRGRP |
                     stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def autoTransfer(real_path: str):
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


def ctrlTransfer(src_folder, dest_folder, 
                linktype, prefix, escape_folders,
                renameflag,
                clean_others,
                replace_CJK,
                refresh_url):
    transfer(src_folder, dest_folder, linktype, prefix,
            escape_folders, '', 
            clean_others, replace_CJK,
            renameflag)
    if refresh_url:
        requests.post(refresh_url)


def transfer(src_folder, dest_folder, 
             linktype, prefix,
             escape_folders, top_files='',
             clean_others_tag = True,
             replace_CJK_tag= False,
             fixseries_tag= False
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
            movie_list = findAllMovies(src_folder, re.split("[,，]", escape_folders))
        else:
            if os.path.exists(top_files):
                clean_others_tag = False
                if os.path.isdir(top_files):
                    movie_list = findAllMovies(top_files, re.split("[,，]", escape_folders))
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
            dest_list = findAllMovies(dest_folder, [])
        else:
            dest_list = []

        todoFiles = []
        for movie_path in movie_list:
            fi = FileInfo(movie_path)
            midfolder = fi.realfolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            fi.updateMidFolder(midfolder)
            if fi.topfolder != '.':
                fi.parse()
            todoFiles.append(fi)

        for currentfile in todoFiles:
            task = taskService.getTask('transfer')
            if task.status == 0:
                return False
            count += 1
            taskService.updateTaskFinished(count, 'transfer')
            log.debug('[!] - ' + str(count) + '/' + total + ' -')
            log.debug("[+] start check [{}] ".format(currentfile.realpath))
            transrecordService.add(currentfile.realpath)

            # 修正后给链接使用的源地址
            link_path = os.path.join(prefix, currentfile.midfolder, currentfile.realname)
            # 处理 midfolder 内特殊内容
            # CMCT组视频文件命名比文件夹命名更好
            if 'CMCT' in currentfile.topfolder:
                matches = [x for x in todoFiles if x.topfolder == currentfile.topfolder]
                # 检测是否有剧集标记
                epfiles = [x for x in matches if x.isepisode]
                if len(matches) > 0 and len(epfiles) == 0:
                    namingfiles = [x for x in matches if 'CMCT' in x.name]
                    if len(namingfiles) == 1:
                        # 非剧集
                        for m in matches:
                            m.topfolder = namingfiles[0].name
                    log.debug("[-] handling cmct midfolder [{}] ".format(midfolder))
            # topfolder 替换中文
            if replace_CJK_tag:
                minlen = 27
                tempmid = currentfile.topfolder
                tempmid = replaceCJK(tempmid)
                tempmid = replaceRegex(tempmid, '^s(\d{2})-s(\d{2})')
                # 可增加过滤词
                grouptags = ['cmct', 'wiki', 'frds', '1080p', 'x264', 'x265']
                for gt in grouptags:
                    if gt in tempmid.lower():
                        minlen += len(gt)
                if len(tempmid) > minlen:
                    log.debug("[-] replace CJK [{}] ".format(tempmid))
                    currentfile.topfolder = tempmid
            # 修正剧集命名
            if fixseries_tag:
                # 判断剧集标记
                if currentfile.isepisode:
                    log.debug("[-] fix series name")
                    # 查询 同级目录下所有视频
                    matches = [x for x in todoFiles if x.folders == currentfile.folders]
                    if len(matches) > 0:
                        # 检查剧集编号，超过2个且不同，连续？才继续处理
                        # 自动推送只有单文件

                        # 检测视频上级目录是否有 season 标记
                        # 上级目录可能是 top 或 second 甚至更低层目录
                        dirfolder = currentfile.folders[len(currentfile.folders)-1]
                        # 根据 season 标记 更新 secondfolder
                        seasonnum = matchSeason(dirfolder)
                        if seasonnum:
                            currentfile.secondfolder = "Season " + str(seasonnum)
                            currentfile.fixEpName(seasonnum)
                        else:
                            # 如果存在大量重复 epnum
                            # 如果检测不到 seasonnum 可能是多季？
                            if currentfile.secondfolder == '':
                                seasonnum = 1
                                currentfile.secondfolder = "Season " + str(seasonnum)
                                currentfile.fixEpName(seasonnum)
                            else:
                                if '花絮' in dirfolder and currentfile.topfolder != '.':
                                    currentfile.secondfolder = "extras"
                                    seasonnum = 0
                                    currentfile.fixEpName(seasonnum)
            # 检测是否是特殊的导评/花絮内容
            # TODO 更多关于花絮的规则
            if currentfile.name == "导演访谈":
                if currentfile.secondfolder == '' and currentfile.topfolder != '.':
                    currentfile.secondfolder = "extras"

            flag_done = False
            if currentfile.topfolder == '.':
                newpath = os.path.join(dest_folder, currentfile.name + currentfile.ext)
            else:
                newpath = os.path.join(dest_folder, currentfile.fixMidFolder(), currentfile.name + currentfile.ext)
            currentfile.updateFinalPath(newpath)
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
                    forceSymlink(link_path, newpath)
                else:
                    forceHardlink(link_path, newpath)

            # 使用最终的文件名
            cleanbyNameSuffix(currentfile.finalfolder, currentfile.name, ext_type)
            oldname = os.path.splitext(currentfile.realname)[0]
            copySubs(currentfile.realfolder, currentfile.finalfolder, oldname, currentfile.name)

            if newpath in dest_list:
                dest_list.remove(newpath)

            log.info("[-] transfered [{}]".format(newpath))
            transrecordService.update(currentfile.realpath, link_path, newpath)

        if clean_others_tag:
            for torm in dest_list:
                log.info("[!] clean extra file: [{}]".format(torm))
                os.remove(torm)
            cleanExtraMedia(dest_folder)
            cleanFolderWithoutSuffix(dest_folder, video_type)

        log.info("transfer finished")
    except Exception as e:
        log.error(e)

    taskService.updateTaskStatus(1, 'transfer')

    return True
