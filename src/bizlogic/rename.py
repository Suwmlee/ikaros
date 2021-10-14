# -*- coding: utf-8 -*-

import os
import re
from ..utils.log import log
from ..utils.filehelper import video_type, ext_type


def file_lists(root):
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.splitext(f)[1].lower() in video_type or os.path.splitext(f)[1].lower() in ext_type:
            total.append(f)
    return total


def filtername(basename, reg):
    """ 正则过滤
    """
    prog = re.compile(reg, re.IGNORECASE | re.X | re.S)
    result = prog.findall(basename)
    return result


def extractep(single: str):
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
    tvs = file_lists(root)
    for name in tvs:
        dirname, basename = os.path.split(name)
        if base in basename:
            newname = basename.replace(base, newfix)
            newfull = os.path.join(dirname, newname)
            os.rename(name, newfull)
            log.info("rename [{}] to [{}]".format(name, newfull))


def findseason(filename:str):
    """
    >>> findseason("Fights.Break.Sphere.2018.S02.WEB-DL.1080p.H264.AAC-TJUPT")
    2
    >>> findseason("疑犯追踪S01-S05.Person.of.Interest.2011-2016.1080p.Blu-ray.x265.AC3￡cXcY@FRDS") is None
    True
    >>> findseason("Yes.Prime.Minister.COMPLETE.PACK.DVD.x264-P2P") is None
    True
    """
    regx = "(?:s|season)(\d{2})"
    nameresult = filtername(filename, regx) 
    if nameresult and len(nameresult) == 1:
        strnum = nameresult[0]
        return int(strnum)
    return None


def regexfilter(basename):
    """ 正则匹配

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

    >>> regexfilter("Shadow.2021.E11.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E11.'
    >>> regexfilter("Shadow.2021.第11集.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '第11集'
    >>> regexfilter("Shadow.2021.E13v2.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E13v2.'
    >>> regexfilter("Shadow.2021.E14(0A).WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E14(0A).'

    >>> regexfilter("S03/Person.of.Interest.EP01.2013.1080p.Blu-ray.x265.10bit.AC3") is None
    True
    >>> regexfilter("Person.of.Interest.S03E01.2013.1080p.Blu-ray.x265.10bit.AC3") is None
    True
    """
    reg = "[\[第 ][0-9.videvoa\(\)]*[\]話话集 ]"
    nameresult = filtername(basename, reg)
    if not nameresult or len(nameresult) == 0:
        reg2 = "\.e[0-9videvoa\(\)]{1,}[.]"
        nameresult = filtername(basename, reg2)
    if nameresult:
        return nameresult[0]
    return None


def renamebyreg(root, reg, prefix, preview: bool = True):
    """ 方法2
    正则匹配替换
    """
    tvs = file_lists(root)
    todolist = []
    newlist = []
    if prefix == '':
        prefix = "S01E"
    for name in tvs:
        dirname, basename = os.path.split(name)
        log.info("开始替换: " + basename)
        if reg == '':
            originep = regexfilter(basename)
        else:
            results = filtername(basename, reg)
            originep = results[0]
        if originep:
            # log.info("提取剧集标签 "+nameresult)
            epresult = extractep(originep)
            if epresult != '':
                log.debug(originep + "   "+epresult)
                if originep[0] == '.':
                    renum = "." + prefix + epresult + "."
                elif originep[0] == '[':
                    renum = "[" + prefix + epresult + "]"
                else:
                    renum = " " + prefix + epresult + " "
                log.debug("替换内容：" + renum)
                newname = basename.replace(originep, renum)
                log.info("替换后:   {}".format(newname))

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
