# -*- coding: utf-8 -*-

import re


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


def matchSeason(filename: str):
    """
    >>> matchSeason("Fights.Break.Sphere.2018.S02.WEB-DL.1080p.H264.AAC-TJUPT")
    2
    >>> matchSeason("疑犯追踪S01-S05.Person.of.Interest.2011-2016.1080p.Blu-ray.x265.AC3￡cXcY@FRDS") is None
    True
    >>> matchSeason("Yes.Prime.Minister.COMPLETE.PACK.DVD.x264-P2P") is None
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

    >>> matchEpPart("生徒会役員共＊ 09 (BDrip 1920x1080 HEVC-YUV420P10 FLAC)")
    ' 09 '
    >>> matchEpPart("[Rip] SLAM DUNK 第013話「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '第013話'
    >>> matchEpPart("[Rip] SLAM DUNK [013]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[013]'
    >>> matchEpPart("[Rip] SLAM DUNK [13.5]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13.5]'
    >>> matchEpPart("[Rip] SLAM DUNK [13v2]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13v2]'
    >>> matchEpPart("[Rip] SLAM DUNK [13(OA)]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)")
    '[13(OA)]'
    >>> matchEpPart("[Neon Genesis Evangelion][23(Video)][BDRIP][1440x1080][H264_FLACx2]")
    '[23(Video)]'
    >>> matchEpPart("[Studio] Fullmetal Alchemist꞉ Brotherhood [01][Ma10p_1080p][x265_flac]")
    '[01]'
    >>> matchEpPart("[raws][Code Geass Lelouch of the Rebellion R2][15][BDRIP][Hi10P FLAC][1920X1080]")
    '[15]'
    >>> matchEpPart("[raws][High School Of The Dead][01][BDRIP][HEVC Main10P FLAC][1920X1080]")
    '[01]'
    >>> matchEpPart("[Studio] Steins;Gate 0 [01][Ma10p_1080p][x265_flac]")
    '[01]'
    >>> matchEpPart("Steins;Gate 2011 EP01 [BluRay 1920x1080p 23.976fps x264-Hi10P FLAC]")
    ' EP01 '
    >>> matchEpPart("Fate Stay Night [Unlimited Blade Works] 2014 - EP01 [BD 1920x1080 AVC-yuv444p10 FLAC PGSx2 Chap]")
    ' EP01 '
    >>> matchEpPart("Fate Zero EP01 [BluRay 1920x1080p 23.976fps x264-Hi10P FLAC PGSx2]")
    ' EP01 '
    >>> matchEpPart("[AI-Raws&ANK-Raws] Initial D First Stage 01 (BDRip 960x720 x264 DTS-HD Hi10P)[044D7040]")
    ' 01 '
    >>> matchEpPart("[AI-Raws&ANK-Raws] Initial D First Stage [05] (BDRip 960x720 x264 DTS-HD Hi10P)[044D7040]")
    '[05]'

    >>> matchEpPart("Shadow.2021.E11.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E11.'
    >>> matchEpPart("Shadow 2021 E11 WEB-DL 4k H265 AAC 2Audio")
    ' E11 '
    >>> matchEpPart("Shadow.2021.第11集.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '第11集'
    >>> matchEpPart("Shadow.2021.E13v2.WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E13v2.'
    >>> matchEpPart("Shadow.2021.E14(OA).WEB-DL.4k.H265.60fps.AAC.2Audio")
    '.E14(OA).'
    >>> matchEpPart("S03/Person.of.Interest.EP01.2013.1080p.Blu-ray.x265.10bit.AC3")
    '.EP01.'
    >>> matchEpPart("Slam.Dunk.22.Ma10p.1080p.x265.flac")
    '.22.'

    >>> matchEpPart("Person.of.Interest.S03E01.2013.1080p.Blu-ray.x265.10bit.AC3") is None
    True
    """
    regexs = [
        "第\d*[話话集]",
        "[ ]ep?[0-9.\(videoa\)]*[ ]",
        "\.ep?[0-9\(videoa\)]*\.",
        "\.\d{2,3}(?:v\d)?[\(videoa\)]*\.",
        "[ ]\d{2,3}(?:\.\d|v\d)?[\(videoa\)]*[ ]",
        "\[(?:e|ep)?[0-9.v]*(?:\(oa\)|\(video\))?\]",
    ]
    for regex in regexs:
        results = regexMatch(basename, regex)
        if results and len(results) == 1:
            return results[0]
    return None


def matchSeries(basename):
    regstr = "s(\d{1,2})ep?(\d{1,4})"
    results = regexMatch(basename, regstr)
    if results and len(results) > 0:
        season = int(results[0][0])
        ep = int(results[0][1])
        return season, ep
    return None, None


def simpleMatchEp(basename: str):
    """ 针对已经强制season但未能正常解析出ep的名字
    
    >>> simpleMatchEp("01 呵呵呵")
    1
    >>> simpleMatchEp("02_哈哈哈")
    2
    >>> simpleMatchEp("03.嘿嘿嘿")
    3
    >>> simpleMatchEp("04. 嘿嘿嘿")
    4
    >>> simpleMatchEp("05 - 嘿嘿嘿")
    5
    >>> simpleMatchEp("06")
    6
    """
    if basename.isdigit():
        return int(basename)
    regstr = "^(\d{1,3}) ?(_|-|.)? ?([^\W\d]+)"
    results = re.findall(regstr, basename)
    if results and len(results) == 1:
        epnunm = int(results[0][0])
        return epnunm
    return None


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
