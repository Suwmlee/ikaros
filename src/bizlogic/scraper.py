# -*- coding: utf-8 -*-
'''
'''
import os
import re
import shutil
import requests
from PIL import Image

from ..service.configservice import scrapingConfService, _ScrapingConfigs
from ..utils.log import log
from ..utils.ADC_function import G_USER_AGENT, is_uncensored
from ..utils.filehelper import ext_type, symlink_force, hardlink_force
from ..scrapinglib import get_data_from_json


def escape_path(path, escape_literals: str):
    """ Remove escape literals
    """
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def create_folder(json_data: dict, conf: _ScrapingConfigs):
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
    path = success_folder + '/' + location_rule
    path = trimrightblank(path)
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals)
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + '] ' + title, "/number")
            path = escape_path(path, conf.escape_literals)

            os.makedirs(path)
    return path


def moveFailedFolder(filepath):
    """ 只创建失败文件的硬链接
        每次刮削清空文件夹
    """
    try:
        log.info('[-]Move to Failed folder')
        conf = scrapingConfService.getSetting()
        if conf.main_mode == 1 and (conf.link_type == 1 or conf.link_type == 2):
            (filefolder, name) = os.path.split(filepath)
            newpath = os.path.join(conf.failed_folder, name)
            hardlink_force(filepath, newpath)
    except:
        pass


def get_info(json_data):
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


def trimrightblank(s: str):
    """
    Clear the blank on the right side of the folder name
    """
    if s[-1] == " ":
        return trimrightblank(s[:-1])
    else:
        return s

# =====================资源下载部分===========================

def download_file_with_filename(url, filename, path):
    configProxy = scrapingConfService.getProxySetting()

    if not os.path.exists(path):
        os.makedirs(path)
    headers = {'User-Agent': G_USER_AGENT}
    for i in range(configProxy.retry):
        try:
            if configProxy.enable:
                proxies = configProxy.proxies()
                r = requests.get(url, headers=headers, timeout=configProxy.timeout, proxies=proxies)
                if r == '':
                    log.info('[-]Movie Data not found!')
                    return False
                with open(os.path.join(str(path), filename), "wb") as code:
                    code.write(r.content)
                return True
            else:
                r = requests.get(url, headers=headers, timeout=configProxy.timeout)
                if r == '':
                    log.info('[-]Movie Data not found!')
                    return False
                with open(os.path.join(str(path), filename), "wb") as code:
                    code.write(r.content)
                return True
        except requests.exceptions.RequestException:
            i += 1
            log.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectionError:
            i += 1
            log.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ProxyError:
            i += 1
            log.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectTimeout:
            i += 1
            log.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
    log.info('[-]Connect Failed! Please check your Proxy or Network!')
    return False


def download_poster(path, prefilename, cover_small_url):
    """ Download Poster
    """
    postername = prefilename + '-poster.jpg'
    if download_file_with_filename(cover_small_url, postername, path):
        log.info('[+]Poster Downloaded! ' + path + '/' + postername)
        return True
    else:
        log.info('[+]Download Poster Failed! ' + path + '/' + postername)
        return False


def download_cover(cover_url, prefilename, path):
    """ Download Cover
    """
    fanartname = prefilename + '-fanart.jpg'
    if download_file_with_filename(cover_url, fanartname, path):
        log.info('[+]Cover Downloaded! ' + path + '/' + fanartname)
        shutil.copyfile(path + '/' + fanartname, path + '/' + prefilename + '-thumb.jpg')
        return True
    else:
        log.info('[+]Download Cover Failed! ' + path + '/' + fanartname)
        return False


def download_extrafanart(urls, path, extrafanart_folder):
    j = 1
    path = path + '/' + extrafanart_folder
    for url in urls:
        if download_file_with_filename(url, 'extrafanart-' + str(j)+'.jpg', path):
            log.info('[+]Extrafanart Downloaded! ' + path + '/extrafanart-' + str(j) + '.jpg')
            j += 1
        else:
            log.info('[+]Download Extrafanart Failed! ' + path + '/extrafanart-' + str(j) + '.jpg')
    return True


def create_nfo_file(path, prefilename, json_data, chs_tag, leak_tag, uncensored_tag):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)
    naming_rule = json_data.get('naming_rule')
    actor_list = json_data.get('actor_list')
    tags = json_data.get('tag')
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(str(path), prefilename + ".nfo"), "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print(" <title>" + naming_rule + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>" + outline + "</outline>", file=code)
            print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + prefilename + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + prefilename + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + prefilename + '-fanart.jpg' + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + key + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                pass
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if chs_tag:
                print("  <tag>中文字幕</tag>", file=code)
            if leak_tag:
                print("  <tag>流出</tag>", file=code)
            if uncensored_tag:
                print("  <tag>无码</tag>", file=code)
            try:
                for i in tags:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                pass
            if chs_tag:
                print("  <genre>中文字幕</genre>", file=code)
            if leak_tag:
                print("  <genre>流出</genre>", file=code)
            if uncensored_tag:
                print("  <genre>无码</genre>", file=code)
            try:
                for i in tags:
                    print("  <genre>" + i + "</genre>", file=code)
                print("  <genre>" + series + "</genre>", file=code)
            except:
                pass
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            log.info("[+]Wrote!            " + path + "/" + prefilename + ".nfo")
            return True
    except IOError as e:
        log.error("[-]Write Failed!")
        log.error(e)
        return False
    except Exception as e1:
        log.error("[-]Write Failed!")
        log.error(e1)
        return False


def crop_poster(imagecut, path, prefilename):
    """ crop fanart to poster
    """
    if imagecut == 1:
        try:
            img = Image.open(path + '/' + prefilename + '-fanart.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(path + '/' + prefilename + '-poster.jpg')
            log.info('[+]Image Cutted!     ' + path + '/' + prefilename + '-poster.jpg')
        except:
            log.info('[-]Cover cut failed!')
    elif imagecut == 0: 
        # 复制封面
        shutil.copyfile(path + '/' + prefilename + '-fanart.jpg',
                        path + '/' + prefilename + '-poster.jpg')
        log.info('[+]Image Copyed!     ' + path + '/' + prefilename + '-poster.jpg')


def add_mark(pics, chs_tag, leak_tag, uncensored_tag, count, size):
    """ 
    Add water mark 
    :param chs_tag          中文字幕  bool
    :param leak_tag         流出      bool
    :param uncensored_tag   无码      bool
    :param count            右上 0, 左上 1, 左下 2，右下 3
    :param size             添加的水印相对整图的比例
    """
    mark_type = ''
    if chs_tag:
        mark_type += ',字幕'
    if leak_tag:
        mark_type += ',流出'
    if uncensored_tag:
        mark_type += ',无码'
    if mark_type == '':
        return
    for pic in pics:
        add_mark_thread(pic, chs_tag, leak_tag, uncensored_tag, count, size)
        log.info('[+]Image Add Mark:   ' + mark_type.strip(','))


def add_mark_thread(pic_path, chs_tag, leak_tag, uncensored_tag, count, size):
    img_pic = Image.open(pic_path)
    if chs_tag:
        add_to_pic(pic_path, img_pic, size, count, 1)
        count = (count + 1) % 4
    if leak_tag:
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored_tag:
        add_to_pic(pic_path, img_pic, size, count, 3)
    img_pic.close()


def add_to_pic(pic_path, img_pic, size, count, mode):
    mark_pic_path = ''
    basedir = os.path.abspath(os.path.dirname(__file__))
    if mode == 1:
        mark_pic_path = basedir +'/../images/CNSUB.png'
    elif mode == 2:
        mark_pic_path = basedir +'/../images/LEAK.png'
    elif mode == 3:
        mark_pic_path = basedir +'/../images/UNCENSORED.png'
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


def paste_file_to_folder(filepath, path, prefilename, link_type):
    """   move video and subtitle
    """
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    try:
        newpath = path + '/' + prefilename + houzhui
        if link_type == 1:
            (filefolder, name) = os.path.split(filepath)
            settings = scrapingConfService.getSetting()
            soft_prefix = settings.soft_prefix
            src_folder = settings.scraping_folder
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            soft_path = os.path.join(soft_prefix, midfolder, name)
            if os.path.exists(newpath):
                realpath = os.path.realpath(newpath)
                if realpath == soft_path:
                    log.info("[-]already exists")
                else:
                    os.remove(newpath)
            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            symlink_force(soft_path, newpath)
        elif link_type == 2:
            hardlink_force(filepath, newpath)
        else:
            os.rename(filepath, newpath)
        # 字幕移动
        for subname in ext_type:
            if os.path.exists(filepath.replace(houzhui, subname)):
                os.rename(filepath.replace(houzhui, subname), path + '/' + prefilename + subname)
                log.info('[+]Sub moved!')
        return True, newpath
    except FileExistsError:
        log.error('[-]File Exists! Please check your movie!')
        return False, ''
    except PermissionError:
        log.error('[-]Error! Please run as administrator!')
        return False, ''
    except OSError as oserr:
        log.error('[-]OS Error errno ' + oserr.errno)
        return False, ''


def get_part(filepath):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        log.error("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath)
        return


def core_main(file_path, scrapingnum, cnsubtag, cdnum, conf: _ScrapingConfigs):
    """ 开始刮削
    :param file_path    文件路径
    :param scrapingnum  使用的番号
    :param cnsubtag     是否增加中文标记
    :param cdnum        是否增加多集标识
    :param conf         刮削配置

    番号
    --爬取数据
    --中文/无码等额外信息
    --下载封面--下载预告--下载剧照
    --裁剪出Poster--增加水印
    --生成nfo--移动视频/字幕

    """
    # =======================================================================初始化所需变量
    
    multipart_tag = False
    chs_tag = False
    uncensored_tag = False
    leak_tag = False
    c_word = ''
    part = ''

    # 影片的路径 绝对路径
    filepath = file_path
    number = scrapingnum
    json_data = get_data_from_json(number, conf.website_priority, conf.naming_rule, conf.async_request)

    # Return if blank dict returned (data not found)
    if not json_data:
        log.info('[-]Movie Data not found!')
        moveFailedFolder(filepath)
        return False, ''

    if json_data.get("number") != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data.get("number")
    imagecut = json_data.get('imagecut')
    
    # =======================================================================判断-C,-CD后缀
    if cdnum:
        multipart_tag = True
        part = '-cd' + str(cdnum)
    else:
        if '-CD' in filepath or '-cd' in filepath:
            multipart_tag = True
            part = get_part(filepath)

    if cnsubtag:
        chs_tag = True
        # 中文字幕影片后缀
        c_word = '-C'
    else:
        cnlist = ['-c.', '-C.', '中文', '字幕', '_c.', '_C.']
        for single in cnlist:
            if single in filepath:
                chs_tag = True
                c_word = '-C'
                break

    # 判断是否无码
    if is_uncensored(number):
        uncensored_tag = True

    if '流出' in filepath or '-leak' in filepath:
        leak_tag = True

    # main_mode
    #  1: 创建链接刮削 / Scraping mode
    #       - 1 软链接    - 2 硬链接    - 0 移动文件
    #  2: 整理模式 / Organizing mode ??
    #  3：直接刮削
    if conf.main_mode == 1:
        # 创建文件夹
        path = create_folder(json_data, conf)

        # 文件名
        prefilename = number + c_word
        if multipart_tag:
            # 番号-Tags-Leak-C-CD1
            prefilename += part

        if imagecut == 3:
            if not download_poster(path, prefilename, json_data.get('cover_small')):
                moveFailedFolder(filepath)
        if not download_cover(json_data.get('cover'), prefilename, path):
            moveFailedFolder(filepath)
        if not multipart_tag or part.lower() == '-cd1':
            try:
                if conf.extrafanart_enable and json_data.get('extrafanart'):
                    download_extrafanart(json_data.get('extrafanart'), path, conf.extrafanart_folder)
            except:
                pass

        crop_poster(imagecut, path, prefilename)
        if conf.watermark_enable:
            pics = [path + '/' + prefilename + '-poster.jpg',
                    path + '/' + prefilename + '-thumb.jpg']
            add_mark(pics, chs_tag, leak_tag, uncensored_tag, conf.watermark_location, conf.watermark_size)
        if not create_nfo_file(path, prefilename, json_data, chs_tag, leak_tag, uncensored_tag):
            moveFailedFolder(filepath)

        # 移动文件
        (flag, newpath) = paste_file_to_folder(filepath, path, prefilename, conf.link_type)
        return flag, newpath
    elif conf.main_mode == 2:
        path = create_folder(json_data, conf)
        prefilename = number + c_word
        if multipart_tag:
            prefilename += part
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
        if not multipart_tag or part.lower() == '-cd1':
            try:
                if conf.extrafanart_enable and json_data.get('extrafanart'):
                    download_extrafanart(json_data.get('extrafanart'), path, conf.extrafanart_folder)
            except:
                pass

        crop_poster(imagecut, path, prefilename)
        if conf.watermark_enable:
            pics = [path + '/' + prefilename + '-poster.jpg',
                    path + '/' + prefilename + '-thumb.jpg']
            add_mark(pics, chs_tag, leak_tag, uncensored_tag, conf.watermark_location, conf.watermark_size)
        if not create_nfo_file(path, prefilename, json_data, chs_tag, leak_tag, uncensored_tag):
            moveFailedFolder(filepath)
        
        return True, file_path
    return False, ''
