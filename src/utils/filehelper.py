# -*- coding: utf-8 -*-
import os
import re
import errno
import shutil
from .log import log

video_type = ['.mp4', '.avi', '.rmvb', '.wmv',
              '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso']
ext_type = ['.ass', '.srt', '.sub', '.ssa', '.smi', '.idx', '.sup',
            '.psb', '.usf', '.xss', '.ssf', '.rt', '.lrc', '.sbv', '.vtt', '.ttml']

video_filter = ['*.mp4', '*.avi', '*.rmvb', '*.wmv',
                '*.mov', '*.mkv', '*.flv', '*.ts', '*.webm', '*.iso']
ext_filter = ['*.ass', '*.srt', '*.sub', '*.ssa', '*.smi', '*.idx', '*.sup',
              '*.psb', '*.usf', '*.xss', '*.ssf', '*.rt', '*.lrc', '*.sbv', '*.vtt', '*.ttml']


def CreatFolder(foldername):
    """ 创建文件
    """
    if not os.path.exists(foldername + '/'):
        try:
            os.makedirs(foldername + '/')
        except Exception as e:
            log.info("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            log.error(e)
            return


def CleanFolder(foldername):
    """ 删除并重新创建文件夹
    """
    try:
        shutil.rmtree(foldername)
    except:
        pass
    CreatFolder(foldername)


def cleanfilebysuffix(folder, suffix):
    """ 删除匹配后缀的文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanfilebysuffix(f, suffix)
        elif os.path.splitext(f)[1].lower() in suffix:
            log.info("clean file by suffix [{}]".format(f))
            os.remove(f)


def cleanbyNameSuffix(folder, basename, suffix):
    """ 根据名称和后缀删除文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        fname, fsuffix = os.path.splitext(f)
        if os.path.isdir(f):
            cleanbyNameSuffix(f, basename, suffix)
        elif fsuffix.lower() in suffix and fname.startswith(basename):
            log.debug("clean by name & suffix [{}]".format(f))
            os.remove(f)


def cleanExtraMedia(folder):
    """ 删除多余的媒体文件(没有匹配的视频文件)
    """
    dirs = os.listdir(folder)
    vlists = []
    for vf in dirs:
        if os.path.splitext(vf)[1].lower() in video_type:
            fname, fsuffix = os.path.splitext(vf)
            vlists.append(fname)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f) and file != "extrafanart":
            cleanExtraMedia(f)
        else:
            cleanflag = True
            if file == "fanart.jpg" or file == "poster.jpg":
                cleanflag = False
            else:
                for s in vlists:
                    if file.startswith(s):
                        cleanflag = False
                        break
            if cleanflag:
                log.debug("clean extra media file [{}]".format(f))
                os.remove(file)


def cleanfolderwithoutsuffix(folder, suffix):
    """ 删除内部无匹配后缀的文件的目录
    """
    hassuffix = False
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            hastag = cleanfolderwithoutsuffix(f, suffix)
            if hastag:
                hassuffix = True
            else:
                log.info("clean empty media folder [{}]".format(f))
                shutil.rmtree(f)
        elif os.path.splitext(f)[1].lower() in suffix:
            hassuffix = True
    return hassuffix


def cleanfolderbyfilter(folder, filter):
    """ 根据过滤名删除文件
    
    如果目录下所有文件都被删除，将删除文件夹
    """
    cleanAll = True
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanAll = False
        else:
            if filter in file:
                log.info("clean folder by filter [{}]".format(f))
                os.remove(f)
            else:
                cleanAll = False
    if cleanAll:
        shutil.rmtree(folder)


def cleanscrapingfile(folder, filter):
    """ 根据过滤名删除刮削文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if not os.path.isdir(f):
            if file.startswith(filter):
                log.info("clean scraping file [{}]".format(f))
                os.remove(f)


def symlink_force(srcpath, dstpath):
    """ create symlink
    https://stackoverflow.com/questions/8299386/modifying-a-symlink-in-python
    """
    try:
        os.symlink(srcpath, dstpath)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dstpath)
            os.symlink(srcpath, dstpath)
        else:
            raise e


def hardlink_force(srcpath, dstpath):
    """ create hard link
    """
    try:
        os.link(srcpath, dstpath)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dstpath)
            os.link(srcpath, dstpath)
        else:
            raise e


def replace_CJK(base: str):
    """ try to replace CJK or brackets

    eg: 你好  [4k修复] (实例1)
    """
    tmp = base
    for n in re.findall(r'[\(\[\（](.*?)[\)\]\）]', base):
        if re.findall(r'[\u4e00-\u9fff]+', n):
            cop = re.compile("[\(\[\（]" + n + "[\)\]\）]")
            tmp = cop.sub('', tmp)
    tmp = re.sub(r'[\u4e00-\u9fff]+', '', tmp)
    return tmp
