# -*- coding: utf-8 -*-
"""
    scrapinglib
    
"""
import os
import json
import re
from lxml import etree
from multiprocessing.pool import ThreadPool

from . import airav
from . import avsox
from . import fanza
from . import fc2
from . import jav321
from . import javbus
from . import javdb
from . import mgstage
from . import xcity
# from . import javlib
from . import dlsite
from . import carib
from . import fc2club
from . import mv91
from . import madou
from flask import current_app


def get_data_state(data: dict) -> bool:
    """ check json data
    """
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True


def get_data_from_json(file_number: str, c_sources: str, c_naming_rule, c_multi_threading=False):
    """
    iterate through all services and fetch the data

    single thread is better
    some sites have query limit

    """

    func_mapping = {
        "airav": airav.main,
        "avsox": avsox.main,
        "fc2": fc2.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        # "javlib": javlib.main,
        "dlsite": dlsite.main,
        "carib": carib.main,
        "fc2club": fc2club.main,
        "mv91": mv91.main,
        "madou": madou.main
    }

    # default fetch order list, from the beginning to the end
    sources = c_sources.split(',')
    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    lo_file_number = file_number.lower()
    if "carib" in sources and (re.match(r"^\d{6}-\d{3}", file_number)
    ):
        sources.insert(0, sources.pop(sources.index("carib")))
    elif re.match(r"^\d{5,}", file_number) or "heyzo" in lo_file_number:
        if "javdb" in sources:
            sources.insert(0, sources.pop(sources.index("javdb")))
        if "avsox" in sources:
            sources.insert(0, sources.pop(sources.index("avsox")))
    elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
                                    "siro" in lo_file_number
    ):
        sources.insert(0, sources.pop(sources.index("mgstage")))
    elif "fc2" in lo_file_number:
        if "javdb" in sources:
            sources.insert(0, sources.pop(sources.index("javdb")))
        if "fc2" in sources:
            sources.insert(0, sources.pop(sources.index("fc2")))
        if "fc2club" in sources:
            sources.insert(0, sources.pop(sources.index("fc2club")))
    elif "dlsite" in sources and (
            "rj" in lo_file_number or "vj" in lo_file_number
    ):
        sources.insert(0, sources.pop(sources.index("dlsite")))
    elif re.match(r"^[a-z0-9]{3,}$", lo_file_number):
        if "javdb" in sources:
            sources.insert(0, sources.pop(sources.index("javdb")))
        if "xcity" in sources:
            sources.insert(0, sources.pop(sources.index("xcity")))

    # check sources in func_mapping
    todel = []
    for s in sources:
        if not s in func_mapping:
            current_app.logger.info('[!] Source Not Exist : ' + s)
            todel.append(s)
    for d in todel:
        current_app.logger.info('[!] Remove Source : ' + s)
        sources.remove(d)

    json_data = {}

    if c_multi_threading:
        current_app.logger.info('[+] Multi threading enabled')
        pool = ThreadPool(processes=len(sources))

        # Set the priority of multi-thread crawling and join the multi-thread queue
        for source in sources:
            pool.apply_async(func_mapping[source], (file_number,))

        # Get multi-threaded crawling response
        # !!! Still follow sources sort not the first response
        for source in sources:
            current_app.logger.debug('[-] Check', source)
            json_data = json.loads(pool.apply_async(func_mapping[source], (file_number,)).get())
            # if any service return a valid return, break
            if get_data_state(json_data):
                current_app.logger.info('[-] Matched [{}] in source [{}]'.format(file_number, source))
                break
        pool.close()
        pool.terminate()
    else:
        for source in sources:
            try:
                current_app.logger.debug('[+] Select Source: ' + source)
                json_data = json.loads(func_mapping[source](file_number))
                # if any service return a valid return, break
                if get_data_state(json_data):
                    current_app.logger.info('[-] Matched [{}] in source [{}]'.format(file_number, source))
                    break
            except Exception as err:
                current_app.logger.info('[!] Source error: ' + source)
                current_app.logger.error(err)
                continue

    # Return if data not found in all sources
    if not json_data:
        current_app.logger.info('[-]Movie Number not found!')
        return

    # ================================================网站规则添加结束================================================

    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    director = json_data.get('director')
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    if json_data.get('cover_small'):
        cover_small = json_data.get('cover_small')
    else:
        cover_small = ''

    if json_data.get('trailer'):
        trailer = json_data.get('trailer')
    else:
        trailer = ''

    if json_data.get('extrafanart'):
        extrafanart = json_data.get('extrafanart')
    else:
        extrafanart = ''

    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    while 'XXXX' in tag:
        tag.remove('XXXX')
    while 'xxx' in tag:
        tag.remove('xxx')
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        current_app.logger.info('[-]Movie Number or Title not found!')
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    actor = special_characters_replacement(actor)
    actor_list = [special_characters_replacement(a) for a in actor_list]
    title = special_characters_replacement(title)
    label = special_characters_replacement(label)
    outline = special_characters_replacement(outline)
    series = special_characters_replacement(series)
    studio = special_characters_replacement(studio)
    director = special_characters_replacement(director)
    tag = [special_characters_replacement(t) for t in tag]
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['original_title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    json_data['trailer'] = trailer
    json_data['extrafanart'] = extrafanart
    json_data['label'] = label
    json_data['outline'] = outline
    json_data['series'] = series
    json_data['studio'] = studio
    json_data['director'] = director

    # 统一演员名/tag等
    localPath = os.path.dirname(os.path.abspath(__file__))
    actorPath = os.path.join(localPath, 'mappingtable', 'mapping_actor.xml')
    infoPath = os.path.join(localPath, 'mappingtable', 'mapping_info.xml')
    actor_mapping_data = etree.parse(actorPath)
    info_mapping_data = etree.parse(infoPath)
    try:
        def mappingActor(src):
            if not src:
                return src
            tmp = actor_mapping_data.xpath('a[contains(@keyword, $name)]/@jp', name=src)
            return tmp[0] if tmp else src
        def mappingInfo(src):
            if not src:
                return src
            tmp = info_mapping_data.xpath('a[contains(@keyword, $name)]/@jp', name=src)
            return tmp[0] if tmp else src

        json_data['actor_list'] = [mappingActor(aa) for aa in json_data['actor_list']]
        json_data['actor'] = mappingActor(json_data['actor'])
        json_data['tag'] = [mappingInfo(aa) for aa in json_data['tag']]

        json_data['tag'] = delete_all_elements_in_list("删除", json_data['tag'])
    except Exception as e:
        current_app.logger.info('mapping error')
        current_app.logger.error(e)

    naming_rule = title
    try:
        naming_rule = eval(c_naming_rule)
    except:
        pass
    json_data['naming_rule'] = naming_rule

    return json_data

def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').     # U+2216 SET MINUS @ Basic Multilingual Plane
                replace('/', '∕').       # U+2215 DIVISION SLASH @ Basic Multilingual Plane
                replace(':', '꞉').       # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
                replace('*', '∗').       # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
                replace('?', '？').      # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
                replace('"', '＂').      # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
                replace('<', 'ᐸ').       # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
                replace('>', 'ᐳ').       # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
                replace('|', 'ǀ').       # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
                replace('&lsquo;', '‘'). # U+02018 LEFT SINGLE QUOTATION MARK
                replace('&rsquo;', '’'). # U+02019 RIGHT SINGLE QUOTATION MARK
                replace('&hellip;','…').
                replace('&amp;', '＆')
            )

def delete_all_elements_in_list(string,lists):
    new_lists = []
    for i in lists:
        if i != string:
            new_lists.append(i)
    return new_lists
