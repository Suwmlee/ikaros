# -*- coding: utf-8 -*-
import os
import errno
import shutil


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
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            return


def CleanFolder(foldername):
    """ rm and create folder
    """
    shutil.rmtree(foldername)
    CreatFolder(foldername)


def cleanfilebysuffix(folder, suffix):
    """ 清理指定目录下所有匹配格式文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanfilebysuffix(f, suffix)
        elif os.path.splitext(f)[1].lower() in suffix:
            print("clean file by suffix ")
            os.remove(f)


def cleanfolderwithoutsuffix(folder, suffix):
    """ 清理目录下无匹配文件的目录
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
                print("clean empty media folder")
                shutil.rmtree(f)
        elif os.path.splitext(f)[1].lower() in suffix:
            hassuffix = True
    return hassuffix


def cleanfolderbyfilter(folder, filter):
    """ clean folder by filter
    
    if all files removed, rm folder
    """
    cleanAll = True
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanAll = False
        else:
            if filter in file:
               os.remove(f)
            else:
                cleanAll = False
    if cleanAll:
        shutil.rmtree(folder)


def symlink_force(target, link_name):
    """ create symlink
    https://stackoverflow.com/questions/8299386/modifying-a-symlink-in-python
    """
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def hardlink_force(target, link_name):
    """ create hard link
    """
    try:
        os.link(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.link(target, link_name)
        else:
            raise e
