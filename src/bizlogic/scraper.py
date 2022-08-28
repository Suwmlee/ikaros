# -*- coding: utf-8 -*-
'''
'''
import os
import re
import shutil
from PIL import Image
from lxml import etree
from flask import current_app

from ..service.taskservice import taskService
from ..service.configservice import scrapingConfService, _ScrapingConfigs
from ..utils.filehelper import linkFile, moveSubsbyFilepath
from ..utils.number_parser import FileNumInfo
from ..scrapinglib import search, httprequest


def escapePath(path, escape_literals: str):
    """ Remove escape literals
    """
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def createFolder(json_data: dict, conf: _ScrapingConfigs, extra=False):
    """ 根据json数据创建文件夹
    """
    success_folder = conf.success_folder
    title = json_data.get('title')
    number = json_data.get('number')
    actor = json_data.get('actor')

    location_rule = eval(conf.location_rule, json_data)
    if 'actor' in conf.location_rule and len(actor) > 100:
        location_rule = eval(conf.location_rule.replace("actor", "'多人作品'"), json_data)
    maxlen = conf.max_title_len
    if 'title' in conf.location_rule and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)

    # path为影片+元数据所在目录
    if extra:
        path = os.path.join(success_folder, f'./{location_rule.strip()}', 'extras')
    else:
        path = os.path.join(success_folder, f'./{location_rule.strip()}')
    if not os.path.exists(path):
        path = escapePath(path, conf.escape_literals)
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + '] ' + title, "/number")
            path = escapePath(path, conf.escape_literals)

            os.makedirs(path)
    path = os.path.abspath(path)
    return path


def moveFailedFolder(filepath):
    """ 只创建失败文件的硬链接
        每次刮削清空文件夹
    """
    try:
        current_app.logger.info('[-]Move to Failed folder')
        task = taskService.getTask('scrape')
        conf = scrapingConfService.getConfig(task.cid)
        if conf.main_mode == 1 and (conf.link_type == 1 or conf.link_type == 2):
            (filefolder, name) = os.path.split(filepath)
            newpath = os.path.join(conf.failed_folder, name)
            linkFile(filepath, newpath, 2)
            return newpath
    except:
        return ''


def parseJsonInfo(json_data):
    """   返回json里的数据
    """
    title = json_data.get('title')
    studio = json_data.get('studio')
    year = json_data.get('year')
    outline = json_data.get('outline')
    runtime = json_data.get('runtime')
    director = json_data.get('director')
    actor_photo = json_data.get('actor_photo')
    release = json_data.get('release')
    number = json_data.get('number')
    cover = json_data.get('cover')
    trailer = json_data.get('trailer')
    website = json_data.get('website')
    series = json_data.get('series')
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label


def download_file_with_filename(url, filename, path):
    """ 下载文件
    """
    task = taskService.getTask('scrape')
    configProxy = scrapingConfService.getProxyConfig(task.cid)
    proxies = configProxy.proxies() if configProxy.enable else None
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        r = httprequest.get(url, proxies=proxies, return_type='object')
        if r == '':
            current_app.logger.info('[-] source not found!')
            return False
        with open(os.path.join(path, filename), "wb") as code:
            code.write(r.content)
        return True
    except:
        return False


def download_poster(path, prefilename, cover_small_url):
    """ Download Poster
    """
    postername = prefilename + '-poster.jpg'
    if download_file_with_filename(cover_small_url, postername, path):
        current_app.logger.debug('[+]Poster Downloaded! ' + postername)
        return True
    else:
        current_app.logger.info('[+]Download Poster Failed! ' + postername)
        return False


def download_cover(cover_url, prefilename, path):
    """ Download Cover
    """
    fanartname = prefilename + '-fanart.jpg'
    fanartpath = os.path.join(path, fanartname)
    thumbpath = os.path.join(path, prefilename + '-thumb.jpg')
    if download_file_with_filename(cover_url, fanartname, path):
        current_app.logger.debug('[+]Cover Downloaded! ' + fanartname)
        shutil.copyfile(fanartpath, thumbpath)
        return True
    else:
        current_app.logger.info('[+]Download Cover Failed! ' + fanartname)
        return False


def download_extrafanart(urls, path, extrafanart_folder):
    j = 1
    path = os.path.join(path, extrafanart_folder)
    for url in urls:
        if download_file_with_filename(url, 'extrafanart-' + str(j)+'.jpg', path):
            current_app.logger.debug('[+]Extrafanart Downloaded! extrafanart-' + str(j) + '.jpg')
            j += 1
        else:
            current_app.logger.info('[+]Download Extrafanart Failed! extrafanart-' + str(j) + '.jpg')
    return True


def create_nfo_file(path, prefilename, json_data, numinfo: FileNumInfo):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = parseJsonInfo(json_data)
    naming_rule = json_data.get('naming_rule')
    actor_list = json_data.get('actor_list')
    tags = json_data.get('tag')
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        nfo_path = os.path.join(path, prefilename + ".nfo")

        # KODI内查看影片信息时找不到number，配置naming_rule=number+'#'+title虽可解决
        # 但使得标题太长，放入时常为空的outline内会更适合，软件给outline留出的显示版面也较大
        outline = f"{number}#{outline}"
        with open(nfo_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print("  <title><![CDATA[" + naming_rule + "]]></title>", file=code)
            print("  <originaltitle><![CDATA[" + naming_rule + "]]></originaltitle>", file=code)
            print("  <sorttitle><![CDATA[" + naming_rule + "]]></sorttitle>", file=code)
            print("  <customrating>JP-18+</customrating>", file=code)
            print("  <mpaa>JP-18+</mpaa>", file=code)
            try:
                print("  <set>" + series + "</set>", file=code)
            except:
                print("  <set></set>", file=code)
            print("  <studio>" + studio + "</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline><![CDATA[" + outline + "]]></outline>", file=code)
            print("  <plot><![CDATA[" + outline + "]]></plot>", file=code)
            print("  <runtime>" + runtime + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + prefilename + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + prefilename + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + prefilename + '-fanart.jpg' + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("    <name>" + key + "</name>", file=code)
                    try:
                        print("    <thumb>" + actor_photo.get(str(key)) + "</thumb>", file=code)
                    except:
                        pass
                    print("  </actor>", file=code)
            except:
                pass
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if numinfo.chs_tag:
                print("  <tag>中文字幕</tag>", file=code)
            if numinfo.leak_tag:
                print("  <tag>流出</tag>", file=code)
            if numinfo.uncensored_tag:
                print("  <tag>无码</tag>", file=code)
            if numinfo.hack_tag:
                print("  <tag>破解</tag>", file=code)
            try:
                for i in tags:
                    print("  <tag>" + i + "</tag>", file=code)
                # print("  <tag>" + series + "</tag>", file=code)
            except:
                pass
            if numinfo.chs_tag:
                print("  <genre>中文字幕</genre>", file=code)
            if numinfo.leak_tag:
                print("  <genre>流出</genre>", file=code)
            if numinfo.uncensored_tag:
                print("  <genre>无码</genre>", file=code)
            if numinfo.hack_tag:
                print("  <genre>破解</genre>", file=code)
            try:
                for i in tags:
                    print("  <genre>" + i + "</genre>", file=code)
                # print("  <genre>" + series + "</genre>", file=code)
            except:
                pass
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <releasedate>" + release + "</releasedate>", file=code)
            print("  <release>" + release + "</release>", file=code)
            try:
                source = json_data.get('source')
                if source == 'javdb' or source == 'javlibrary':
                    rating = json_data.get('userrating')
                    votes = json_data.get('uservotes')
                    if source == 'javdb':
                        toprating = 5
                    elif source == 'javlibrary':
                        toprating = 10
                    print(f"""  <rating>{round(rating * 10.0 / toprating, 1)}</rating>
  <criticrating>{round(rating * 100.0 / toprating, 1)}</criticrating>
  <ratings>
    <rating name="{source}" max="{toprating}" default="true">
      <value>{rating}</value>
      <votes>{votes}</votes>
    </rating>
  </ratings>""", file=code)
            except:
                pass
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <trailer>" + trailer + "</trailer>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            current_app.logger.info("[+]Wrote!            " + nfo_path)
            return True
    except Exception as e:
        current_app.logger.error("[-]Write NFO Failed!")
        current_app.logger.error(e)
        return False


def crop_poster(imagecut, path, prefilename):
    """ crop fanart to poster
    """
    fanartpath = os.path.join(path, prefilename + '-fanart.jpg')
    posterpath = os.path.join(path, prefilename + '-poster.jpg')
    if imagecut == 1:
        try:
            img = Image.open(fanartpath)
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(posterpath)
            current_app.logger.debug('[+]Image Cutted!     ' + posterpath)
        except:
            current_app.logger.info('[-]Cover cut failed!')
    elif imagecut == 0:
        # 复制封面
        shutil.copyfile(fanartpath, posterpath)
        current_app.logger.debug('[+]Image Copyed!     ' + posterpath)


def add_mark(pics, numinfo: FileNumInfo, count, size):
    """ 
    Add water mark 
    :param numinfo          番号信息,内有详细Tag信息
    :param count            右上:0 左上:1 左下:2 右下:3
    :param size             添加的水印相对整图的比例
    """
    mark_type = ''
    if numinfo.chs_tag:
        mark_type += ',字幕'
    if numinfo.leak_tag:
        mark_type += ',流出'
    if numinfo.uncensored_tag:
        mark_type += ',无码'
    if numinfo.hack_tag:
        mark_type += ',破解'
    if mark_type == '':
        return
    for pic in pics:
        add_mark_thread(pic, numinfo, count, size)
        current_app.logger.debug('[+]Image Add Mark:   ' + mark_type.strip(','))


def add_mark_thread(pic_path, numinfo: FileNumInfo, count, size):
    img_pic = Image.open(pic_path)
    if numinfo.chs_tag:
        add_to_pic(pic_path, img_pic, size, count, 1)
        count = (count + 1) % 4
    if numinfo.leak_tag:
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if numinfo.uncensored_tag:
        add_to_pic(pic_path, img_pic, size, count, 3)
        count = (count + 1) % 4
    if numinfo.hack_tag:
        add_to_pic(pic_path, img_pic, size, count, 4)
    img_pic.close()


def add_to_pic(pic_path, img_pic, size, count, mode):
    mark_pic_path = ''
    basedir = os.path.abspath(os.path.dirname(__file__))
    if mode == 1:
        mark_pic_path = basedir + '/../images/CNSUB.png'
    elif mode == 2:
        mark_pic_path = basedir + '/../images/LEAK.png'
    elif mode == 3:
        mark_pic_path = basedir + '/../images/UNCENSORED.png'
    elif mode == 4:
        mark_pic_path = basedir + '/../images/HACK.png'
    img_subt = Image.open(mark_pic_path)
    scroll_high = int(img_pic.height / size)
    scroll_wide = int(scroll_high * img_subt.width / img_subt.height)
    img_subt = img_subt.resize((scroll_wide, scroll_high), Image.ANTIALIAS)
    r, g, b, a = img_subt.split()  # 获取颜色通道，保持png的透明性
    # 封面四个角的位置
    pos = [
        {'x': img_pic.width - scroll_wide, 'y': 0},
        {'x': 0, 'y': 0},
        {'x': 0, 'y': img_pic.height - scroll_high},
        {'x': img_pic.width - scroll_wide, 'y': img_pic.height - scroll_high},
    ]
    img_pic.paste(img_subt, (pos[count]['x'], pos[count]['y']), mask=a)
    img_pic.save(pic_path, quality=95)


def paste_file_to_folder(filepath, path, prefilename, link_type, extra=False):
    """   move video and subtitle
    """
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    try:
        copyTag = True
        newpath = os.path.join(path, prefilename + houzhui)
        if link_type == 1:
            (filefolder, name) = os.path.split(filepath)
            task = taskService.getTask('scrape')
            config = scrapingConfService.getConfig(task.cid)
            soft_prefix = config.soft_prefix
            src_folder = config.scraping_folder
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            soft_path = os.path.join(soft_prefix, midfolder, name)
            linkFile(soft_path, newpath, 1)
        elif link_type == 2:
            linkFile(filepath, newpath, 2)
        else:
            copyTag = False
            os.rename(filepath, newpath)
        moveSubsbyFilepath(filepath, newpath, copyTag)
        return True, newpath
    except FileExistsError:
        current_app.logger.error('[-]File Exists! Please check your movie!')
        return False, ''
    except PermissionError:
        current_app.logger.error('[-]Error! Please run as administrator!')
        return False, ''
    except OSError as oserr:
        current_app.logger.error(oserr)
        return False, ''


def core_main(filepath, numinfo: FileNumInfo, conf: _ScrapingConfigs, specifiedsource=None, specifiedurl=None):
    """ 开始刮削
    :param filepath     文件路径
    :param numinfo      番号信息
    :param conf         刮削配置

    番号
    --爬取数据
    --中文/无码等额外信息
    --下载封面--下载预告--下载剧照
    --裁剪出Poster--增加水印
    --生成nfo
    --移动视频/字幕

    """

    number = numinfo.num
    # json_data = get_data_from_json(number, conf.site_sources, conf.naming_rule, conf.async_request)
    c_sources = conf.site_sources
    if not c_sources:
        c_sources = "javlibrary,javdb,javbus,airav,fanza,xcity,jav321,mgstage,fc2,avsox,dlsite,carib,madou,mv91,getchu,gcolle"
    task = taskService.getTask('scrape')
    configProxy = scrapingConfService.getProxyConfig(task.cid)
    proxies = configProxy.proxies() if configProxy.enable else None
    json_data = search(number, c_sources,
                       specifiedSource=specifiedsource, specifiedUrl=specifiedurl,
                       proxies=proxies, morestoryline=conf.morestoryline)
    # Return if blank dict returned (data not found)
    if not json_data or json_data.get('number') == '' or json_data.get('title') == '':
        current_app.logger.error('[-]Movie Data not found!')
        return False, moveFailedFolder(filepath)

    json_data = fixJson(json_data, conf.naming_rule)

    if json_data.get("number") != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data.get("number")
    imagecut = json_data.get('imagecut')

    # main_mode
    #  1: 创建链接刮削 / Scraping mode
    #       - 1 软链接    - 2 硬链接    - 0 移动文件
    #  2: 整理模式 / Organizing mode ??
    #  3: 直接刮削
    if conf.main_mode == 1:
        # 创建文件夹
        path = createFolder(json_data, conf, numinfo.special)
        # 文件名
        prefilename = numinfo.fixedName()

        if not numinfo.special:
            if imagecut == 3:
                if not download_poster(path, prefilename, json_data.get('cover_small')):
                    moveFailedFolder(filepath)
            if not download_cover(json_data.get('cover'), prefilename, path):
                moveFailedFolder(filepath)
            if numinfo.isPartOneOrSingle():
                try:
                    if conf.extrafanart_enable and json_data.get('extrafanart'):
                        download_extrafanart(json_data.get('extrafanart'), path, conf.extrafanart_folder)
                except:
                    pass

            crop_poster(imagecut, path, prefilename)
            if conf.watermark_enable:
                pics = [os.path.join(path, prefilename + '-poster.jpg'),
                        os.path.join(path, prefilename + '-thumb.jpg')]
                add_mark(pics, numinfo, conf.watermark_location, conf.watermark_size)
            if not create_nfo_file(path, prefilename, json_data, numinfo):
                moveFailedFolder(filepath)

        # 移动文件
        (flag, newpath) = paste_file_to_folder(filepath, path, prefilename, conf.link_type)
        return flag, newpath
    elif conf.main_mode == 2:
        path = createFolder(json_data, conf, numinfo.special)
        prefilename = numinfo.fixedName()
        (flag, newpath) = paste_file_to_folder(filepath, path, prefilename, conf.link_type)
        return flag, newpath
    elif conf.main_mode == 3:
        path = os.path.dirname(filepath)
        name = os.path.basename(filepath)
        prefilename = os.path.splitext(name)[0]

        if imagecut == 3:
            if not download_poster(path, prefilename, json_data.get('cover_small')):
                moveFailedFolder(filepath)
        if not download_cover(json_data.get('cover'), prefilename, path):
            moveFailedFolder(filepath)
        if numinfo.isPartOneOrSingle():
            try:
                if conf.extrafanart_enable and json_data.get('extrafanart'):
                    download_extrafanart(json_data.get('extrafanart'), path, conf.extrafanart_folder)
            except:
                pass

        crop_poster(imagecut, path, prefilename)
        if conf.watermark_enable:
            pics = [os.path.join(path, prefilename + '-poster.jpg'),
                    os.path.join(path, prefilename + '-thumb.jpg')]
            add_mark(pics, numinfo, conf.watermark_location, conf.watermark_size)
        if not create_nfo_file(path, prefilename, json_data, numinfo):
            moveFailedFolder(filepath)

        return True, filepath
    return False, ''


def fixJson(json_data, c_naming_rule):
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

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
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
    json_data['actor'] = ','.join(actor_list)
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
    actorPath = os.path.join(localPath, '../mappingtable', 'mapping_actor.xml')
    infoPath = os.path.join(localPath, '../mappingtable', 'mapping_info.xml')
    actor_mapping_data = etree.parse(actorPath)
    info_mapping_data = etree.parse(infoPath)
    try:
        def mappingkey(data, key):
            # 忽略大小写
            return data.xpath('a[contains(translate(@keyword,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"), $name)]/@jp', name=key.lower())

        def mappingActor(src):
            if not src:
                return src
            tmp = mappingkey(actor_mapping_data, src)
            if tmp and len(tmp) == 1:
                return tmp[0]
            if '(' in src or '（' in src:
                csrc = cleanBrackets(src)
                tmp2 = mappingkey(actor_mapping_data, csrc)
                if tmp2 and len(tmp2) == 1:
                    return tmp2[0]
                allbrackets = getBrackets(src)
                for b in allbrackets:
                    tmp3 = mappingkey(actor_mapping_data, b)
                    if tmp3 and len(tmp3) == 1:
                        return tmp3[0]
            forcesrc = ',' + src + ','
            tmp4 = mappingkey(actor_mapping_data, forcesrc)
            if tmp4 and len(tmp4) == 1:
                return tmp4[0]
            return src
            
        def mappingInfo(src):
            if not src:
                return src
            tmp = mappingkey(info_mapping_data, src)
            return tmp[0] if tmp else src

        json_data['actor_list'] = [mappingActor(aa) for aa in json_data['actor_list']]
        json_data['actor'] = ','.join(json_data['actor_list'])
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


def cleanBrackets(s):
    ext = re.sub('\(.*?\)', '', s)
    ext = re.sub('（.*?）', '', ext)
    return ext.strip()


def getBrackets(s):
    bra = re.compile(r'[(（](.*?)[)）]', re.S)
    return re.findall(bra, s)


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
            replace('&lsquo;', '‘').  # U+02018 LEFT SINGLE QUOTATION MARK
            replace('&rsquo;', '’').  # U+02019 RIGHT SINGLE QUOTATION MARK
            replace('&hellip;', '…').
            replace('&amp;', '＆')
            )


def delete_all_elements_in_list(string, lists):
    new_lists = []
    for i in lists:
        if i != string:
            new_lists.append(i)
    return new_lists
