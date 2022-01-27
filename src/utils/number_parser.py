import os
import re
from flask import current_app

G_spat = re.compile(
    "^22-sht\.me|-fhd|_fhd|^fhd_|^fhd-|-hd|_hd|^hd_|^hd-|-sd|_sd|-1080p|_1080p|-720p|_720p|^hhd800\.com@|-uncensored|_uncensored|-leak|_leak",
    re.IGNORECASE)


class FileNumInfo():
    """ 解析文件番号信息
    """

    def __init__(self, filepath: str):
        self.num = get_number(filepath)

        self.chs_tag = False
        self.uncensored_tag = False
        self.leak_tag = False
        self.multipart_tag = False
        self.part = ''

        if self.num and is_uncensored(self.num):
            self.uncensored_tag = True
        filepath = filepath.lower()
        if '流出' in filepath or '-leak' in filepath or '_leak' in filepath \
                or '-uncensored' in filepath or '_uncensored' in filepath:
            self.leak_tag = True
        cnlist = ['中文', '字幕', '-c.', '_c.', '_c_', '-c-']
        for single in cnlist:
            if single in filepath:
                self.chs_tag = True
                break
        if '_cd' in filepath or '-cd' in filepath:
            self.part = get_part(filepath)
            if self.part:
                self.multipart_tag = True

    def fixedName(self):
        name = self.num
        if self.uncensored_tag:
            name += '-uncensored'
        if self.leak_tag:
            name += '-leak'
        if self.chs_tag:
            name += '-C'
        if self.multipart_tag:
            name += self.part
        return name

    def updateCD(self, cdnum):
        self.multipart_tag = True
        self.part = '-CD' + str(cdnum)

    def isPartOneOrSingle(self):
        if not self.multipart_tag or self.part == '-CD1' or self.part == '-CD01':
            return True
        return False


def get_number(file_path: str) -> str:
    """ 获取番号
    """
    try:
        basename = os.path.basename(file_path)
        (filename, ext) = os.path.splitext(basename)
        file_number = get_number_by_dict(filename)
        if file_number:
            return file_number
        elif '-' in filename or '_' in filename:  # 普通提取番号 主要处理包含减号-和_的番号
            filename = G_spat.sub("", filename)
            # TODO more filter
            filename = str(re.sub("(-|_|.)x26(4|5)", "", filename, flags=re.IGNORECASE))
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))  # 去除文件名中时间
            lower_check = filename.lower()
            if 'fc2' in lower_check:
                filename = lower_check.replace('ppv', '').replace('--', '-').replace('_', '-').upper()
            filename = re.sub("(-|_)cd\d{1,2}", "", filename, flags=re.IGNORECASE)
            file_number = str(re.search(r'\w+(-|_)\w+', filename, re.A).group())
            file_number = re.sub("(-|_)c$", "", file_number, flags=re.IGNORECASE)
            return file_number.upper()
        else:  # 提取不含减号-的番号，FANZA CID
            # 欧美番号匹配规则
            oumei = re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', basename)
            if oumei:
                return oumei.group()
            try:
                return str(
                    re.findall(r'(.+?)\.',
                               str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', basename).group()))).strip(
                    "['']").replace('_', '-')
            except:
                return str(re.search(r'(.+?)\.', basename)[0])
    except Exception as e:
        current_app.logger.error(e)
        return


# 按javdb数据源的命名规范提取number
G_TAKE_NUM_RULES = {
    'tokyo.*hot': lambda x: str(re.search(r'(cz|gedo|k|n|red-|se)\d{2,4}', x, re.I).group()),
    'carib': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('_', '-'),
    '1pon|mura|paco': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('-', '_'),
    '10mu': lambda x: str(re.search(r'\d{6}(-|_)\d{2}', x, re.I).group()).replace('-', '_'),
    'x-art': lambda x: str(re.search(r'x-art\.\d{2}\.\d{2}\.\d{2}', x, re.I).group()),
    'xxx-av': lambda x: ''.join(['xxx-av-', re.findall(r'xxx-av[^\d]*(\d{3,5})[^\d]*', x, re.I)[0]]),
    'heydouga': lambda x: 'heydouga-' + '-'.join(re.findall(r'(\d{4})[\-_](\d{3,4})[^\d]*', x, re.I)[0]),
    'heyzo': lambda x: 'HEYZO-' + re.findall(r'heyzo[^\d]*(\d{4})', x, re.I)[0]
}


def get_number_by_dict(filename: str) -> str:
    try:
        for k, v in G_TAKE_NUM_RULES.items():
            if re.search(k, filename, re.I):
                return v(filename)
    except:
        pass
    return None


class Cache_uncensored_conf:
    prefix = None

    def is_empty(self):
        return bool(self.prefix is None)

    def set(self, v: list):
        if not v or not len(v) or not len(v[0]):
            raise ValueError('input prefix list empty or None')
        s = v[0]
        if len(v) > 1:
            for i in v[1:]:
                s += f"|{i}.+"
        self.prefix = re.compile(s, re.I)

    def check(self, number):
        if self.prefix is None:
            raise ValueError('No init re compile')
        return self.prefix.match(number)


G_cache_uncensored_conf = Cache_uncensored_conf()


def is_uncensored(number):
    if re.match(
        r'[\d-]{4,}|\d{6}_\d{2,3}|(cz|gedo|k|n|red-|se)\d{2,4}|heyzo.+|xxx-av-.+|heydouga-.+|x-art\.\d{2}\.\d{2}\.\d{2}',
        number,
        re.I
    ):
        return True
    uncensored_prefix = "S2M,BT,LAF,SMD,SMBD,SM3D2DBD,SKY-,SKYHD,CWP,CWDV,CWBD,CW3D2DBD,MKD,MKBD,MXBD,MK3D2DBD,MCB3DBD,MCBD,RHJ,RED"
    if G_cache_uncensored_conf.is_empty():
        G_cache_uncensored_conf.set(uncensored_prefix.split(','))
    return G_cache_uncensored_conf.check(number)


def get_part(filepath: str):
    try:
        prog = re.compile("(?:-|_)cd\d{1,2}", re.IGNORECASE | re.X | re.S)
        result = prog.findall(filepath)
        if result:
            part = str(result[0]).upper().replace('_', '-')
            return part
    except:
        return
