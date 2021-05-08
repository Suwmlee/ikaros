# -*- coding: utf-8 -*-

import os
import re
from ..utils.filehelper import video_type, ext_type


def file_lists(root):
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.splitext(f)[1] in video_type or os.path.splitext(f)[1] in ext_type:
            total.append(f)
    return total


def filtername(basename, reg):
    """ 正则过滤
    """
    prog = re.compile(reg, re.IGNORECASE | re.X | re.S)
    result = prog.findall(basename)
    return result


def extractep(src):
    """ 提取剧集编号
    """
    result = src.lstrip('第.EPpe\[ ')
    result = result.rstrip('話话]. ')
    return result


def rename(root, base, newfix):
    tvs = file_lists(root)
    for name in tvs:
        dirname, basename = os.path.split(name)
        if base in basename:
            newname = basename.replace(base, newfix)
            newfull = os.path.join(dirname, newname)
            os.rename(name, newfull)
            print("rename [{}] to [{}]".format(name, newfull))


def renamebyreg(root, reg, reg2, prefix, preview: bool):
    tvs = file_lists(root)
    todolist = []
    newlist = []
    # reg = "[\[第 ][0-9.videvoa\(\)]*[\]話话 ]"
    for name in tvs:
        dirname, basename = os.path.split(name)
        print("开始. : "+basename)

        nameresult = filtername(basename, reg)
        if not nameresult or len(nameresult) == 0:
            # reg2 = "\.e[0-9videvoa\(\)]{1,}[.]"
            nameresult = filtername(basename, reg2)
        if nameresult and len(nameresult) == 1:
            print("提取剧集标签 "+nameresult[0])
            epresult = extractep(nameresult[0])
            if epresult != '':
                print("   "+epresult)
                renum = "." + prefix + epresult + "."
                print("替换内容：" + renum)
                newname = srcname.replace(nameresult[0], renum)
                print("rename [{}] to [{}]".format(basename, newname))

                if not preview:
                    newfull = os.path.join(dirname, newname)
                    os.rename(name, newfull)

                todolist.append(basename)
                newlist.append(newname)
    ret = dict()
    ret['todo'] = todolist
    ret['prefix'] = newlist
    return ret


if __name__ == "__main__":

    """
[ANK-Raws] 生徒会役員共＊ 09 (BDrip 1920x1080 HEVC-YUV420P10 FLAC)
[Rip] SLAM DUNK 第013話「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Rip] SLAM DUNK [013]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Rip] SLAM DUNK [E013]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Rip] SLAM DUNK [13.5]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Rip] SLAM DUNK [13v2]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Rip] SLAM DUNK [13(OA)]「湘北VS陵南 燃える主将!」(BDrip 1440x1080 H264 FLAC)
[Neon Genesis Evangelion][23(Video)][BDRIP][1440x1080][H264_FLACx2]
[Studio] Fullmetal Alchemist꞉ Brotherhood [01][Ma10p_1080p][x265_flac]
[raws][Code Geass Lelouch of the Rebellion][01][BDRIP][Hi10P FLAC][1920X1080]
[raws][Code Geass Lelouch of the Rebellion R2][15][BDRIP][Hi10P FLAC][1920X1080]
Sunshine.Police.2020.E24.WEB-DL.4k.H265.HDR.AAC
Shadow.2021.E11.WEB-DL.4k.H265.60fps.AAC.2Audio
Shadow.2021.e12.WEB-DL.4k.H265.60fps.AAC.2Audio
Shadow.2021.E13v2.WEB-DL.4k.H265.60fps.AAC.2Audio
Shadow.2021.E14(0A).WEB-DL.4k.H265.60fps.AAC.2Audio
Shadow.2021.E.WEB-DL.4k.H265.60fps.AAC.2Audio
Person.of.Interest.S03E01.2013.1080p.Blu-ray.x265.10bit.AC3
    """

