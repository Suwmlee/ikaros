# -*- coding: utf-8 -*-

import os
from flask import current_app
from ..utils.filehelper import video_type, ext_type
from ..utils.regex import extractEpNum, matchEpPart, regexMatch


def findAllMatchedFiles(root):
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.splitext(f)[1].lower() in video_type or os.path.splitext(f)[1].lower() in ext_type:
            total.append(f)
    return total


def rename(root, base, newfix):
    """ 方法1
    字符替换
    """
    tvs = findAllMatchedFiles(root)
    for name in tvs:
        dirname, basename = os.path.split(name)
        if base in basename:
            newname = basename.replace(base, newfix)
            newfull = os.path.join(dirname, newname)
            os.rename(name, newfull)
            current_app.logger.info("rename [{}] to [{}]".format(name, newfull))


def renamebyreg(root, reg, prefix, preview: bool = True):
    """ 方法2
    正则匹配替换
    """
    tvs = findAllMatchedFiles(root)
    todolist = []
    newlist = []
    if prefix == '':
        prefix = "S01E"
    for name in tvs:
        dirname, basename = os.path.split(name)
        current_app.logger.info("开始替换: " + basename)
        if reg == '':
            originep = matchEpPart(basename)
        else:
            results = regexMatch(basename, reg)
            originep = results[0]
        if originep:
            # current_app.logger.info("提取剧集标签 "+nameresult)
            epresult = extractEpNum(originep)
            if epresult != '':
                current_app.logger.debug(originep + "   "+epresult)
                if originep[0] == '.':
                    renum = "." + prefix + epresult + "."
                elif originep[0] == '[':
                    renum = "[" + prefix + epresult + "]"
                else:
                    renum = " " + prefix + epresult + " "
                newname = basename.replace(originep, renum)
                current_app.logger.info("修正后:   {}".format(newname))

                if not preview:
                    newfull = os.path.join(dirname, newname)
                    os.rename(name, newfull)

                todolist.append(basename)
                newlist.append(newname)

    ret = dict()
    ret['todo'] = todolist
    ret['prefix'] = newlist
    return ret
