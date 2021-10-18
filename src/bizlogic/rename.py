# -*- coding: utf-8 -*-

import os
import re
from flask import current_app
from ..utils.filehelper import video_type, ext_type


def findAllMatchedFiles(root):
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.splitext(f)[1].lower() in video_type or os.path.splitext(f)[1].lower() in ext_type:
            total.append(f)
    return total


def regexMatch(basename, reg):
    """ 正则匹配
    """
    prog = re.compile(reg, re.IGNORECASE | re.X | re.S)
    result = prog.findall(basename)
    return result


def extractEpNum(single: str):
    """ 提取剧集编号
    1. 头尾匹配 空格 [] 第话
    2. 剔除头尾修饰字符
    3. 校验含有数字
    4. 如果不包含E,仍需校验是否是年份，个位数
    """
    left = single[0]
    right = single[-1:]
    if left == right or (left == '[' and right == ']') or (left == '第' and right in '話话集'):

        result = single.lstrip('第.EPep\[ ')
        result = result.rstrip('話话集]. ')

        if bool(re.search(r'\d', result)):
            if not bool(re.search(r'[Ee]', single)):
                if len(result) == 1:
                    return None
                match = re.match(r'.*([1-3][0-9]{3})', result)
                if match:
                    return None
                return result
            else:
                return result
    return None


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


def matchSeason(filename:str):
    """
    >>> findseason("Fights.Break.Sphere.2018.S02.WEB-DL.1080p.H264.AAC-TJUPT")
    2
    >>> findseason("疑犯追踪S01-S05.Person.of.Interest.2011-2016.1080p.Blu-ray.x265.AC3￡cXcY@FRDS") is None
    True
    >>> findseason("Yes.Prime.Minister.COMPLETE.PACK.DVD.x264-P2P") is None
    True
    """
    regx = "(?:s|season)(\d{2})"
    nameresult = regexMatch(filename, regx) 
    if nameresult and len(nameresult) == 1:
        strnum = nameresult[0]
        return int(strnum)
    return None


def matchEpPart(basename):
    """ 正则匹配单集编号

    >>> regexfilter("生徒会役員共＊ 09 (BDrip 1920x1080 HEVC-YUV420P10 FLAC)")
    ' 09 '
    >>> regexfilter("[Rip] SLAM DUNK 第013話「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '第013話'
    >>> regexfilter("[Rip] SLAM DUNK [013]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[013]'
    >>> regexfilter("[Rip] SLAM DUNK [13.5]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13.5]'
    >>> regexfilter("[Rip] SLAM DUNK [13v2]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13v2]'
    >>> regexfilter("[Rip] SLAM DUNK [13(OA)]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13(OA)]'
    >>> regexfilter("[Neon Genesis Evangelion][23(Video)][BDRIP][1440x1080][H264_FLACx2]")
    '[23(Video)]'
    >>> regexfilter("[Studio] Fullmetal Alchemist꞉ Brotherhood [01][Ma10p_1080p][x265_flac]")
    '[01]'
    >>> regexfilter("[raws][Code Geass Lelouch of the Rebellion R2][15][BDRIP][Hi10P FLAC][1920X1080]")
    '[15]'
    >>> regexfilter("[raws][High School Of The Dead][01][BDRIP][HEVC Main10P FLAC][1920X1080]")
    '[01]'
    >>> regexfilter("[Studio] Steins;Gate 0 [01][Ma10p_1080p][x265_flac]")
    '[01]'
    >>> regexfilter("Steins;Gate 2011 EP01 [BluRay 1920x1080p 23.976fps x264-Hi10P FLAC]")
    ' EP01 '
    >>> regexfilter("Fate Stay Night [Unlimited Blade Works] 2014 - EP01 [BD 1920x1080 AVC-yuv444p10 FLAC PGSx2 Chap]")
    ' EP01 '
    >>> regexfilter("Fate Zero EP01 [BluRay 1920x1080p 23.976fps x264-Hi10P FLAC PGSx2]")
    ' EP01 '
    
    >>> regexfilter("Shadow.2021.E11.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E11.'
    >>> regexfilter("Shadow 2021 E11 WEB-DL 4k H265 AAC 2Audio")
    ' E11 '
    >>> regexfilter("Shadow.2021.第11集.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '第11集'
    >>> regexfilter("Shadow.2021.E13v2.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E13v2.'
    >>> regexfilter("Shadow.2021.E14(OA).WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E14(OA).'
    >>> regexfilter("S03/Person.of.Interest.EP01.2013.1080p.Blu-ray.x265.10bit.AC3")
    '.EP01.'

    >>> regexfilter("Person.of.Interest.S03E01.2013.1080p.Blu-ray.x265.10bit.AC3") is None
    True
    """
    regexs = [
        "第\d*[話话集]",
        "\[(?:e|ep)?[0-9.\(videoa\)]*\]",
        "[ ]ep?[0-9.\(videoa\)]*[ ]",
        "[.]ep?[0-9\(videoa\)]*[.]",
        "[ ]\d{2,3}(?:\.\d|v\d)?[\(videoa\)]*[ ]"
    ]
    for regex in regexs:
        results = regexMatch(basename, regex)
        if results and len(results) == 1:
            return results[0]
    return None


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


# if __name__ == "__main__":
#     import doctest
#     doctest.testmod(verbose=True)
