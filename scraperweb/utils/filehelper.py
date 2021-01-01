# -*- coding: utf-8 -*-
import os
import shutil


video_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV', '.MOV', '.MKV', '.FLV', '.TS', '.WEBM', '.iso', '.ISO']
ext_type = ['.ass', '.srt', '.sub']

video_filter = ['*.mp4', '*.avi', '*.rmvb', '*.wmv', '*.mov', '*.mkv', '*.flv', '*.ts', '*.webm', '*.iso']
ext_filter = ['*.ass', '*.srt', '*.sub']


def cleanfilebysuffix(folder, suffix):
    """ 清理指定目录下所有匹配格式文件
    """
    dirs = os.listdir(folder)
    for file in dirs:
        f = os.path.join(folder, file)
        if os.path.isdir(f):
            cleanfilebysuffix(f, suffix)
        elif os.path.splitext(f)[1] in suffix:
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
        elif os.path.splitext(f)[1] in suffix:
            hassuffix = True
    return hassuffix
