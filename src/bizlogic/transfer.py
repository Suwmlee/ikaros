# -*- coding: utf-8 -*-
'''
'''
import os
import re
import time

from .mediaserver import refreshMediaServer
from ..service.configservice import transConfigService
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService
from ..utils.regex import extractEpNum, matchSeason, matchEpPart, matchSeries, simpleMatchEp
from ..utils.filehelper import linkFile, video_type, ext_type, replaceRegex, cleanFolderWithoutSuffix, \
    replaceCJK, cleanbyNameSuffix, cleanExtraMedia, moveSubs
from flask import current_app


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
    locked = False
    forcedseason = False
    originep = ''
    season = None
    epnum = None
    forcedname = ''

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
        folders = os.path.normpath(mid).split(os.path.sep)
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

    def updateForcedname(self, name):
        self.forcedname = name

    def fixFinalName(self):
        if self.forcedname != "":
            return self.forcedname + self.ext
        else:
            return self.name + self.ext

    def updateFinalPath(self, path):
        self.finalpath = path
        self.finalfolder = os.path.dirname(path)

    def parse(self):
        # 正确的剧集命名
        season, ep = matchSeries(self.name)
        if isinstance(season, int) and season > -1 and isinstance(ep, int) and ep > -1:
            self.isepisode = True
            self.season = season
            self.epnum = ep
            self.originep = 'Pass'
            return
        # 是否是需要修正的剧集命名
        originep = matchEpPart(self.name)
        if originep:
            epresult = extractEpNum(originep)
            if epresult:
                self.isepisode = True
                self.originep = originep
                self.epnum = epresult

    def fixEpName(self, season):
        if not self.epnum and self.forcedseason:
            current_app.logger.debug("强制`season`后,尝试获取`ep`")
            sep = simpleMatchEp(self.name)
            if sep:
                self.epnum = sep
                self.originep = 'Pass'
            else:
                return
        if isinstance(self.epnum, int):
            prefix = "S%02dE%02d" % (season, self.epnum)
        else:
            prefix = "S%02dE" % (season) + self.epnum

        if self.originep == 'Pass':
            if prefix in self.name:
                return
            else:
                self.name = prefix
        else:
            if self.originep[0] == '.':
                renum = "." + prefix + "."
            elif self.originep[0] == '[':
                renum = " " + prefix + " "
            else:
                renum = " " + prefix + " "
            current_app.logger.debug("替换内容:" + renum)
            newname = self.name.replace(self.originep, renum)
            self.name = newname
            current_app.logger.info("替换后:   {}".format(newname))


def findAllVideos(root, src_folder, escape_folder, mode=1):
    """ find all videos
    mode:
    :1  返回 FileInfo 合集
    :2  返回 realPath 合集
    """
    if os.path.basename(root) in escape_folder:
        return []
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += findAllVideos(f, src_folder, escape_folder, mode)
        elif os.path.splitext(f)[1].lower() in video_type:
            if mode == 1:
                fi = FileInfo(f)
                midfolder = fi.realfolder.replace(src_folder, '').lstrip("\\").lstrip("/")
                fi.updateMidFolder(midfolder)
                if fi.topfolder != '.':
                    fi.parse()
                total.append(fi)
            elif mode == 2:
                total.append(f)
    return total


def autoTransfer(cid, real_path: str):
    """ 自动转移
    返回
    0:  转移失败
    1:  转移成功,推送媒体库
    2:  转移成功,推送媒体库异常
    """
    conf = transConfigService.getConfigById(cid)
    try:
        current_app.logger.debug("任务详情: 自动转移")
        if not transfer(conf.source_folder, conf.output_folder,
                        conf.linktype, conf.soft_prefix,
                        conf.escape_folder, real_path,
                        False, conf.replace_CJK, conf.fix_series):
            return 0
        if conf.refresh_url:
            if not refreshMediaServer(conf.refresh_url):
                return 2
        return 1
    except:
        return 0


def ctrlTransfer(src_folder, dest_folder,
                 linktype, prefix, escape_folders,
                 specified_files, fix_series,
                 clean_others,
                 replace_CJK,
                 refresh_url):
    transfer(src_folder, dest_folder, linktype, prefix,
             escape_folders, specified_files,
             clean_others, replace_CJK,
             fix_series)
    if refresh_url:
        refreshMediaServer(refresh_url)


def transfer(src_folder, dest_folder,
             linktype, prefix,
             escape_folders, specified_files='',
             clean_others_tag=True,
             simplify_tag=False,
             fixseries_tag=False
             ):
    """
    如果 specified_files 有值，则使用 specified_files 过滤文件且不清理其他文件
    """

    task = taskService.getTask('transfer')
    if task.status == 2:
        return False
    taskService.updateTaskStatus(task, 2)

    try:
        movie_list = []

        if not specified_files or specified_files == '':
            movie_list = findAllVideos(src_folder, src_folder, re.split("[,，]", escape_folders))
        else:
            if not os.path.exists(specified_files):
                specified_files = os.path.join(src_folder, specified_files)
                if not os.path.exists(specified_files):
                    taskService.updateTaskStatus(task, 1)
                    current_app.logger.error("[!] specified_files not exists")
                    return False
            clean_others_tag = False
            if os.path.isdir(specified_files):
                movie_list = findAllVideos(specified_files, src_folder, re.split("[,，]", escape_folders))
            else:
                tf = FileInfo(specified_files)
                midfolder = tf.realfolder.replace(src_folder, '').lstrip("\\").lstrip("/")
                tf.updateMidFolder(midfolder)
                if tf.topfolder != '.':
                    tf.parse()
                movie_list.append(tf)
        count = 0
        total = str(len(movie_list))
        taskService.updateTaskNum(task, total)
        current_app.logger.debug('[+] Find  ' + total+'  movies')

        # 硬链接直接使用源目录
        if linktype == 1:
            prefix = src_folder
        # 清理目标目录下的文件:视频 字幕
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        if clean_others_tag:
            dest_list = findAllVideos(dest_folder, '', [], 2)
        else:
            dest_list = []

        for currentfile in movie_list:
            if not isinstance(currentfile, FileInfo):
                continue
            task = taskService.getTask('transfer')
            if task.status == 0:
                return False
            count += 1
            taskService.updateTaskFinished(task, count)
            current_app.logger.debug('[!] - ' + str(count) + '/' + total + ' -')
            current_app.logger.debug("[+] start check [{}] ".format(currentfile.realpath))

            # 修正后给链接使用的源地址
            link_path = os.path.join(prefix, currentfile.midfolder, currentfile.realname)

            currentrecord = transrecordService.add(currentfile.realpath)
            currentrecord.srcfolder = src_folder
            # 忽略标记，直接下一个
            if currentrecord.ignored:
                continue
            # 锁定
            if currentrecord.locked:
                # TODO
                currentfile.locked = True
            # 记录优先
            # 如果是剧集，season优先
            if currentrecord.topfolder and currentrecord.topfolder != '.':
                currentfile.topfolder = currentrecord.topfolder
            if currentrecord.secondfolder:
                currentfile.secondfolder = currentrecord.secondfolder

            if currentrecord.isepisode:
                currentfile.isepisode = True
                if isinstance(currentrecord.season, int) and currentrecord.season > -1:
                    currentfile.season = currentrecord.season
                    currentfile.forcedseason = True
                if isinstance(currentrecord.episode, int) and currentrecord.episode > -1:
                    currentfile.epnum = currentrecord.episode
                elif isinstance(currentrecord.episode, str) and currentrecord != '':
                    currentfile.epnum = currentrecord.episode
            elif not fixseries_tag:
                currentfile.isepisode = False
            if currentrecord.forcedname:
                currentfile.updateForcedname(currentrecord.forcedname)

            # 优化命名
            naming(currentfile, movie_list, simplify_tag, fixseries_tag)

            if currentfile.topfolder == '.':
                newpath = os.path.join(dest_folder, currentfile.fixFinalName())
            else:
                newpath = os.path.join(dest_folder, currentfile.fixMidFolder(), currentfile.fixFinalName())
            currentfile.updateFinalPath(newpath)
            if linktype == 0:
                linkFile(link_path, newpath, 1)
            else:
                linkFile(link_path, newpath, 2)

            # 使用最终的文件名
            cleanbyNameSuffix(currentfile.finalfolder, currentfile.name, ext_type)
            oldname = os.path.splitext(currentfile.realname)[0]
            moveSubs(currentfile.realfolder, currentfile.finalfolder, oldname, currentfile.name)

            if os.path.exists(currentrecord.destpath) and newpath != currentrecord.destpath:
                # 清理之前转移的文件
                transrecordService.deleteRecordFiles(currentrecord, False)

            if newpath in dest_list:
                dest_list.remove(newpath)

            current_app.logger.info("[-] transfered [{}]".format(newpath))
            transrecordService.updateRecord(currentrecord, link_path, newpath, currentrecord.status,
                                            currentfile.topfolder, currentfile.secondfolder,
                                            currentfile.isepisode, currentfile.season, currentfile.epnum)
            # need rest 100ms
            time.sleep(0.1)

        if clean_others_tag:
            for torm in dest_list:
                current_app.logger.info("[!] remove other file: [{}]".format(torm))
                os.remove(torm)
            cleanExtraMedia(dest_folder)
            cleanFolderWithoutSuffix(dest_folder, video_type)

        current_app.logger.info("transfer finished")
    except Exception as e:
        current_app.logger.error(e)

    taskService.updateTaskStatus(task, 1)

    return True


def naming(currentfile: FileInfo, movie_list: list, simplify_tag, fixseries_tag):
    # 处理 midfolder 内特殊内容
    # CMCT组视频文件命名比文件夹命名更好
    if 'CMCT' in currentfile.topfolder and not currentfile.locked:
        matches = [x for x in movie_list if x.topfolder == currentfile.topfolder]
        # 检测是否有剧集标记
        epfiles = [x for x in matches if x.isepisode]
        if len(matches) > 0 and len(epfiles) == 0:
            namingfiles = [x for x in matches if 'CMCT' in x.name]
            if len(namingfiles) == 1:
                # 非剧集
                for m in matches:
                    m.topfolder = namingfiles[0].name
            current_app.logger.debug("[-] handling cmct midfolder [{}] ".format(currentfile.midfolder))
    # topfolder
    if simplify_tag and not currentfile.locked:
        minlen = 20
        tempmid = currentfile.topfolder
        tempmid = replaceCJK(tempmid)
        tempmid = replaceRegex(tempmid, '^s(\d{2})-s(\d{2})')
        # TODO 可增加过滤词
        grouptags = ['cmct', 'wiki', 'frds', '1080p', 'x264', 'x265']
        for gt in grouptags:
            if gt in tempmid.lower():
                minlen += len(gt)
        if len(tempmid) > minlen:
            current_app.logger.debug("[-] replace CJK [{}] ".format(tempmid))
            currentfile.topfolder = tempmid
    # 修正剧集命名
    if fixseries_tag:
        if currentfile.isepisode:
            current_app.logger.debug("[-] fix series name")
            # 检测是否有修正记录
            if isinstance(currentfile.season, int) and isinstance(currentfile.epnum, int) \
                    and currentfile.season > -1 and currentfile.epnum > -1:
                current_app.logger.debug("[-] directly use record")
                if currentfile.season == 0:
                    currentfile.secondfolder = "Specials"
                else:
                    currentfile.secondfolder = "Season " + str(currentfile.season)
                try:
                    currentfile.fixEpName(currentfile.season)
                except:
                    currentfile.name = "S%02dE%02d" % (currentfile.season, currentfile.epnum)
            else:
                if isinstance(currentfile.season, int) and currentfile.season > -1:
                    seasonnum = currentfile.season
                else:
                    # 检测视频上级目录是否有 season 标记
                    dirfolder = currentfile.folders[len(currentfile.folders)-1]
                    # 根据 season 标记 更新 secondfolder
                    seasonnum = matchSeason(dirfolder)
                if seasonnum:
                    currentfile.season = seasonnum
                    currentfile.secondfolder = "Season " + str(seasonnum)
                    currentfile.fixEpName(seasonnum)
                else:
                    # 如果检测不到 seasonnum 可能是多季？默认第一季
                    if currentfile.secondfolder == '':
                        currentfile.season = 1
                        currentfile.secondfolder = "Season " + str(1)
                        currentfile.fixEpName(1)
                    # TODO 更多关于花絮的规则
                    else:
                        try:
                            dirfolder = currentfile.folders[len(currentfile.folders)-1]
                            if '花絮' in dirfolder and currentfile.topfolder != '.':
                                currentfile.secondfolder = "Specials"
                                currentfile.season = 0
                                currentfile.fixEpName(0)
                        except Exception as ex:
                            current_app.logger.error(ex)
