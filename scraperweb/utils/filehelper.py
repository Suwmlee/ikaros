# -*- coding: utf-8 -*-
import os
import glob


video_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV', '.MOV', '.MKV', '.FLV', '.TS', '.WEBM', '.iso', '.ISO']
ext_type = ['.nfo', '.ass', '.srt', '.sub']

video_filter = ['*.mp4', '*.avi', '*.rmvb', '*.wmv', '*.mov', '*.mkv', '*.flv', '*.ts', '*.webm', '*.iso']
ext_filter = ['*.nfo', '*.ass', '*.srt', '*.sub']


def cleanallfileinfolder(folder, suffix):
    """ 清理指定目录下所有匹配格式文件
    """
    for s in suffix:
        for infile in glob.glob(os.path.join(folder, suffix)):
            os.remove(infile)

