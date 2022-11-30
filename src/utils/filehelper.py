# -*- coding: utf-8 -*-
import os
import pathlib
import re
import errno
import shutil
import stat
import logging
from flask import current_app

video_type = ['.mp4', '.avi', '.rmvb', '.wmv',
              '.mov', '.mkv', '.flv', '.ts', '.m2ts','.webm', '.iso']
ext_type = ['.ass', '.srt', '.sub', '.ssa', '.smi', '.idx', '.sup',
            '.psb', '.usf', '.xss', '.ssf', '.rt', '.lrc', '.sbv', '.vtt', '.ttml']

video_filter = ['*.mp4', '*.avi', '*.rmvb', '*.wmv',
                '*.mov', '*.mkv', '*.flv', '*.ts', '*.m2ts', '*.webm', '*.iso']
ext_filter = ['*.ass', '*.srt', '*.sub', '*.ssa', '*.smi', '*.idx', '*.sup',
              '*.psb', '*.usf', '*.xss', '*.ssf', '*.rt', '*.lrc', '*.sbv', '*.vtt', '*.ttml']


def creatFolder(foldername):
    """ 创建文件
    """
    if not os.path.exists(foldername + '/'):
        try:
            os.makedirs(foldername + '/')
        except Exception as e:
            logger().info("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            logger().error(e)
            return


def checkFolderhasMedia(folder):
    """ 检测文件夹内是否有视频文件
    """
    if not os.path.isdir(folder):
        if os.path.exists(folder):
            return True
        return False
    for root, dirs, files in os.walk(folder, topdown=False):
        for file in files:
            if file.lower().endswith(tuple(video_type)):
                return True
    return False


def cleanFolder(foldername):
    """ 删除并重新创建文件夹
    """
    try:
        shutil.rmtree(foldername)
    except:
        pass
    creatFolder(foldername)


def cleanbySuffix(folder, suffix):
    """ 删除匹配后缀的文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanbySuffix(f, suffix)
        elif os.path.splitext(f)[1].lower() in suffix:
            logger().info("clean file by suffix [{}]".format(f))
            os.remove(f)


def cleanbyNameSuffix(folder, basename, suffix):
    """ 根据名称和后缀删除文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        fname, fsuffix = os.path.splitext(file)
        if os.path.isdir(f):
            cleanbyNameSuffix(f, basename, suffix)
        elif fsuffix.lower() in suffix and fname.startswith(basename):
            logger().debug("clean by name & suffix [{}]".format(f))
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
            if file.lower().startswith(('fanart', 'poster', 'tvshow', 'season', 'landscape')):
                cleanflag = False
            else:
                for s in vlists:
                    if file.startswith(s):
                        cleanflag = False
                        break
            if cleanflag:
                logger().debug("clean extra media file [{}]".format(f))
                os.remove(f)


def cleanFolderWithoutSuffix(folder, suffix):
    """ 删除无匹配后缀文件的目录
    """
    hassuffix = False
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            hastag = cleanFolderWithoutSuffix(f, suffix)
            if hastag:
                hassuffix = True
        elif os.path.splitext(f)[1].lower() in suffix:
            hassuffix = True
    if not hassuffix:
        logger().info("clean empty media folder [{}]".format(folder))
        shutil.rmtree(folder)
    return hassuffix


def cleanFolderbyFilter(folder, filter):
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
                logger().info("clean folder by filter [{}]".format(f))
                os.remove(f)
            else:
                cleanAll = False
    if cleanAll:
        shutil.rmtree(folder)


def cleanFilebyFilter(folder, filter):
    """ 根据过滤名删除文件

    只当前目录,不递归删除
    未含分集标识的filter不能删除带有分集标识的文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if not os.path.isdir(f):
            if file.startswith(filter):
                # 未分集到分集 重复删除分集内容
                if '-CD' in file.upper():
                    if '-CD' in filter.upper():
                        logger().info("clean file [{}]".format(f))
                        os.remove(f)
                else:
                    logger().info("clean file [{}]".format(f))
                    os.remove(f)


def moveSubs(srcfolder, destfolder, basename, newname, saved=True):
    """ 移动字幕
    :param saved    True: 复制字幕  False: 移动字幕
    """
    dirs = os.listdir(srcfolder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type and path.startswith(basename):
            src_file = os.path.join(srcfolder, item)
            newpath = path.replace(basename, newname)
            logger().debug("[-] - copy sub  " + src_file)
            newfile = os.path.join(destfolder, newpath + ext)
            if saved:
                shutil.copyfile(src_file, newfile)
            else:
                shutil.move(src_file, newfile)
            # modify permission
            os.chmod(newfile, stat.S_IRWXU | stat.S_IRGRP |
                     stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def moveSubsbyFilepath(srcpath, destpath, saved=True):
    """ 根据文件名匹配字幕，并移动到指定目录
    :param saved    True: 复制字幕  False: 移动字幕
    """
    srcfolder, srcname = os.path.split(srcpath)
    srcbasename, srcext = os.path.splitext(srcname)
    destfolder, destname = os.path.split(destpath)
    destbasename, destext = os.path.splitext(destname)
    moveSubs(srcfolder, destfolder, srcbasename, destbasename, saved)


def forceSymlink(srcpath, dstpath):
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


def forceHardlink(srcpath, dstpath):
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

def checkFileExists(filepath):
    """ 检测文件是否存在
    软/硬链接
    """
    if os.path.exists(filepath):
        return True
    elif pathlib.Path(filepath).is_symlink():
        return True
    else:
        return False

def linkFile(srcpath, dstpath, linktype=1):
    """ 链接文件

    params: linktype: `1` 软链接 `2` 硬链接

    https://stackoverflow.com/questions/41941401/how-to-find-out-if-a-folder-is-a-hard-link-and-get-its-real-path
    """
    if os.path.exists(dstpath) and os.path.samefile(srcpath, dstpath) and linktype == 2:
        logger().debug("[!] same file already exists")
    elif pathlib.Path(dstpath).is_symlink() and os.readlink(dstpath) == srcpath and linktype == 1:
        logger().debug("[!] link file already exists")
    else:
        dstfolder = os.path.dirname(dstpath)
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)
        logger().debug("[-] create link from [{}] to [{}]".format(srcpath, dstpath))
        if linktype == 1:
            forceSymlink(srcpath, dstpath)
        else:
            forceHardlink(srcpath, dstpath)


def replaceCJK(base: str):
    """ 尝试替换 CJK 字符
    https://stackoverflow.com/questions/1366068/whats-the-complete-range-for-chinese-characters-in-unicode
    
    https://www.unicode.org/charts/charindex.html

    eg: 你好  [4k修复] (实例1)
    """
    tmp = base
    for n in re.findall('[\(\[\（](.*?)[\)\]\）]', base):
        if re.findall('[\u3000-\u33FF\u4e00-\u9fff]+', n):
            cop = re.compile("[\(\[\（]" + n + "[\)\]\）]")
            tmp = cop.sub('', tmp)
    tmp = re.sub('[\u3000-\u33FF\u4e00-\u9fff]+', '', tmp)
    tmp = re.sub(r'(\W)\1+', r'\1', tmp).lstrip(' !?@#$.:：]）)').rstrip(' !?@#$.:：[(（')
    return tmp


def replaceRegex(base: str, regex: str):
    cop = re.compile(regex, re.IGNORECASE | re.X | re.S)
    base = cop.sub('', base)
    base = re.sub(r'(\W)\1+', r'\1', base).lstrip(' !?@#$.:：]）)').rstrip(' !?@#$.:：[(（')
    return base


def logger() -> logging.Logger:
    """
    prevent app_context error
    """
    if current_app:
        return current_app.logger
    return logging.getLogger('src')
