import json
import os.path
import re
import shutil
import platform

from PIL import Image

from ..service.configservice import scrapingConfService, _ScrapingConfigs
from ..utils.wlogger import wlogger
from ..utils.ADC_function import *
from ..utils.filehelper import ext_type, symlink_force, hardlink_force

# =========website========
from ..scrapinglib import avsox
from ..scrapinglib import fanza
from ..scrapinglib import fc2
from ..scrapinglib import jav321
from ..scrapinglib import javbus
from ..scrapinglib import javdb
from ..scrapinglib import mgstage
from ..scrapinglib import xcity
# from ..scrapinglib import javlib
from ..scrapinglib import dlsite
from ..scrapinglib import airav
from ..scrapinglib import carib
from ..scrapinglib import fc2club


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    """ 只创建失败文件的硬链接
        每次刮削清空文件夹
    """
    try:
        wlogger.info('[-]Move to Failed folder')
        (filefolder, name) = os.path.split(filepath)
        newpath = os.path.join(failed_folder, name)
        hardlink_force(filepath, newpath)
    except:
        pass


def get_data_from_json(file_number, conf: _ScrapingConfigs):
    """
    iterate through all services and fetch the data 
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
        "fc2club": fc2club.main
    }

    # default fetch order list, from the beginning to the end
    sources = conf.website_priority.split(',')
    if not len(conf.website_priority) > 60:
        # if the input file name matches certain rules,
        # move some web service to the beginning of the list
        lo_file_number = file_number.lower()
        if "carib" in sources and (re.match(r"^\d{6}-\d{3}", file_number)
        ):
            sources.insert(0, sources.pop(sources.index("carib")))
        elif "avsox" in sources and (re.match(r"^\d{5,}", file_number) or
                                     "heyzo" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("javdb")))
            sources.insert(1, sources.pop(sources.index("avsox")))
        elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
                                       "siro" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("mgstage")))
        elif "fc2" in sources and ("fc2" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("javdb")))
            sources.insert(1, sources.pop(sources.index("fc2")))
            sources.insert(2, sources.pop(sources.index("fc2club")))
        elif "dlsite" in sources and (
                "rj" in lo_file_number or "vj" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("dlsite")))

    json_data = {}
    
    for source in sources:
        try:
            json_data = json.loads(func_mapping[source](file_number))
            # if any service return a valid return, break
            if get_data_state(json_data):
                break
        except:
            break

    # Return if data not found in all sources
    if not json_data:
        return

    # ================================================网站规则添加结束================================================

    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    if json_data.get('cover_small') == None:
        cover_small = ''
    else:
        cover_small = json_data.get('cover_small')

    trailer = ''
    extrafanart = ''

    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')

    # ====================处理异常字符 END================== #\/:*?"<>|

    # ===  替换Studio片假名
    studio = studio.replace('アイエナジー','Energy')
    studio = studio.replace('アイデアポケット','Idea Pocket')
    studio = studio.replace('アキノリ','AKNR')
    studio = studio.replace('アタッカーズ','Attackers')
    studio = re.sub('アパッチ.*','Apache',studio)
    studio = studio.replace('アマチュアインディーズ','SOD')
    studio = studio.replace('アリスJAPAN','Alice Japan')
    studio = studio.replace('オーロラプロジェクト・アネックス','Aurora Project Annex')
    studio = studio.replace('クリスタル映像','Crystal 映像')
    studio = studio.replace('グローリークエスト','Glory Quest')
    studio = studio.replace('ダスッ！','DAS！')
    studio = studio.replace('ディープス','DEEP’s')
    studio = studio.replace('ドグマ','Dogma')
    studio = studio.replace('プレステージ','PRESTIGE')
    studio = studio.replace('ムーディーズ','MOODYZ')
    studio = studio.replace('メディアステーション','宇宙企画')
    studio = studio.replace('ワンズファクトリー','WANZ FACTORY')
    studio = studio.replace('エスワン ナンバーワンスタイル','S1')
    studio = studio.replace('エスワンナンバーワンスタイル','S1')
    studio = studio.replace('SODクリエイト','SOD')
    studio = studio.replace('サディスティックヴィレッジ','SOD')
    studio = studio.replace('V＆Rプロダクツ','V＆R PRODUCE')
    studio = studio.replace('V＆RPRODUCE','V＆R PRODUCE')
    studio = studio.replace('レアルワークス','Real Works')
    studio = studio.replace('マックスエー','MAX-A')
    studio = studio.replace('ピーターズMAX','PETERS MAX')
    studio = studio.replace('プレミアム','PREMIUM')
    studio = studio.replace('ナチュラルハイ','NATURAL HIGH')
    studio = studio.replace('マキシング','MAXING')
    studio = studio.replace('エムズビデオグループ','M’s Video Group')
    studio = studio.replace('ミニマム','Minimum')
    studio = studio.replace('ワープエンタテインメント','WAAP Entertainment')
    studio = re.sub('.*/妄想族','妄想族',studio)
    studio = studio.replace('/',' ')
    # ===  替换Studio片假名 END

    location_rule = eval(conf.location_rule)

    if 'actor' in conf.location_rule and len(actor) > 100:
        wlogger.info(conf.location_rule)
        location_rule = eval(conf.location_rule.replace("actor", "'多人作品'"))
    maxlen = conf.max_title_len
    if 'title' in conf.location_rule and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list

    json_data['trailer'] = ''
    json_data['extrafanart'] = ''

    naming_rule = ""
    for i in conf.naming_rule.split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
        else:
            naming_rule += json_data.get(i)
    json_data['naming_rule'] = naming_rule
    return json_data


def get_info(json_data):  # 返回json里的数据
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


def small_cover_check(path, number, cover_small, c_word, conf, filepath, failed_folder):
    download_file_with_filename(cover_small, number + c_word + '-poster.jpg', path, conf, filepath, failed_folder)
    wlogger.info('[+]Image Downloaded! ' + path + '/' + number + c_word + '-poster.jpg')


def create_folder(success_folder, location_rule, json_data, conf):
    """ 根据json数据创建文件夹
    """
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)
    if len(location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor", "'manypeople'", 3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
    path = trimblank(path)
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals)
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ')-' + title, "/number")
            path = escape_path(path, conf.escape_literals)

            os.makedirs(path)
    return path


def trimblank(s: str):
    """
    Clear the blank on the right side of the folder name
    """
    if s[-1] == " ":
        return trimblank(s[:-1])
    else:
        return s

# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!


def download_file_with_filename(url, filename, path, conf, filepath, failed_folder):
    configProxy = scrapingConfService.getProxySetting()

    for i in range(configProxy.retry):
        try:
            if configProxy.enable:
                if not os.path.exists(path):
                    os.makedirs(path)
                proxies = configProxy.proxies()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=configProxy.timeout, proxies=proxies)
                if r == '':
                    wlogger.info('[-]Movie Data not found!')
                    return
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, timeout=configProxy.timeout, headers=headers)
                if r == '':
                    wlogger.info('[-]Movie Data not found!')
                    return
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            wlogger.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectionError:
            i += 1
            wlogger.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ProxyError:
            i += 1
            wlogger.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectTimeout:
            i += 1
            wlogger.info('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
    wlogger.info('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, failed_folder)
    return


# 封面是否下载成功，否则移动到failed
def image_download(cover, number, c_word, path, conf, filepath, failed_folder):
    if download_file_with_filename(cover, number + c_word + '-fanart.jpg', path, conf, filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    configProxy = scrapingConfService.getProxySetting()
    for i in range(configProxy.retry):
        if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
            wlogger.info('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(cover, number + c_word + '-fanart.jpg', path, conf, filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
        return
    wlogger.info('[+]Image Downloaded! ' + path + '/' + number + c_word + '-fanart.jpg')
    shutil.copyfile(path + '/' + number + c_word + '-fanart.jpg', path + '/' + number + c_word + '-thumb.jpg')


def print_files(path, c_word, naming_rule, part, chs_tag, json_data, filepath, failed_folder, tag, actor_list, liuchu, uncensored):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)

    try:
        if not os.path.exists(path):
            os.makedirs(path)
        filename = number + part + c_word
        # TODO: 直接刮削文件名临时修改
        if os.path.dirname(filepath) == path:
            name = os.path.basename(filepath)
            filename  = os.path.splitext(name)[0]
        with open(path + "/" + filename + ".nfo", "wt", encoding='UTF-8') as code:
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
            print("  <poster>" + number + c_word + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + number + c_word + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + number + c_word + '-fanart.jpg' + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + key + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                aaaa = ''
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if chs_tag:
                print("  <tag>中文字幕</tag>", file=code)
            if liuchu == '流出':
                print("  <tag>流出</tag>", file=code)
            if uncensored == 1:
                print("  <tag>无码</tag>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                aaaaa = ''
            if chs_tag:
                print("  <genre>中文字幕</genre>", file=code)
            if liuchu == '流出':
                print("  <genre>流出</genre>", file=code)
            if uncensored == 1:
                print("  <genre>无码</genre>", file=code)
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
                print("  <genre>" + series + "</genre>", file=code)
            except:
                aaaaaaaa = ''
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            wlogger.info("[+]Wrote!            " + path + "/" + number + part + c_word + ".nfo")
    except IOError as e:
        wlogger.info("[-]Write Failed!")
        wlogger.error(e)
        moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e1:
        wlogger.error(e1)
        wlogger.info("[-]Write Failed!")
        moveFailedFolder(filepath, failed_folder)
        return


def cutImage(imagecut, path, number, c_word):
    if imagecut == 1:  # 剪裁大封面
        try:
            img = Image.open(path + '/' + number + c_word + '-fanart.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(path + '/' + number + c_word + '-poster.jpg')
            wlogger.info('[+]Image Cutted!     ' + path + '/' + number + c_word + '-poster.jpg')
        except:
            wlogger.info('[-]Cover cut failed!')
    elif imagecut == 0:  # 复制封面
        shutil.copyfile(path + '/' + number + c_word + '-fanart.jpg', path + '/' + number + c_word + '-poster.jpg')
        wlogger.info('[+]Image Copyed!     ' + path + '/' + number + c_word + '-poster.jpg')

# 此函数从gui版copy过来用用
# 参数说明
# poster_path
# thumb_path
# chs_tag        中文字幕  bool
# leak_tag       流出      bool
# uncensored_tag 无码      bool
# ========================================================================加水印


def add_mark(poster_path, thumb_path, chs_tag, leak, uncensored, conf):
    mark_type = ''
    if chs_tag:
        mark_type += ',字幕'
    if leak:
        mark_type += ',流出'
    if uncensored:
        mark_type += ',无码'
    if mark_type == '':
        return
    add_mark_thread(thumb_path, chs_tag, leak, uncensored, conf)
    print('[+]Thumb Add Mark:   ' + mark_type.strip(','))
    add_mark_thread(poster_path, chs_tag, leak, uncensored, conf)
    print('[+]Poster Add Mark:  ' + mark_type.strip(','))


def add_mark_thread(pic_path, chs_tag, leak, uncensored, conf):
    img_pic = Image.open(pic_path)
    # 获取自定义位置
    # 右上 0, 左上 1, 左下 2，右下 3
    count = conf.watermark_location
    # 添加的水印相对整图的比例
    size = conf.watermark_size
    if chs_tag:
        add_to_pic(pic_path, img_pic, size, count, 1)  # 添加
        count = (count + 1) % 4
    if leak == 1 or leak == '1':
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored == 1 or uncensored == '1':
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
# ========================结束=================================


def paste_file_to_folder(filepath, path, number, c_word, conf):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    try:
        newpath = path + '/' + number + c_word + houzhui
        if conf.link_type == 1:
            (filefolder, name) = os.path.split(filepath)
            settings = scrapingConfService.getSetting()
            soft_prefix = settings.soft_prefix
            src_folder = settings.scraping_folder
            dest_folder = settings.success_folder
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            soft_path = os.path.join(soft_prefix, midfolder, name)
            if os.path.exists(newpath):
                realpath = os.path.realpath(newpath)
                if realpath == soft_path:
                    print("already exists")
                else:
                    os.remove(newpath)
            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            symlink_force(soft_path, newpath)
        elif conf.link_type == 2:
            hardlink_force(filepath, newpath)
        else:
            os.rename(filepath, newpath)
        # 字幕移动
        for subname in ext_type:
            if os.path.exists(filepath.replace(houzhui, subname)):
                os.rename(filepath.replace(houzhui, subname), path + '/' + number + c_word + subname)
                print('[+]Sub moved!')
        return True, newpath
    except FileExistsError:
        wlogger.info('[-]File Exists! Please check your movie!')
        wlogger.info('[-]move to the root folder of the program.')
        return False, ''
    except PermissionError:
        wlogger.info('[-]Error! Please run as administrator!')
        return False, ''


def paste_file_to_folder_mode2(filepath, path, multi_part, number, part, c_word, conf):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        number += part  # 这时number会被附加上CD1后缀
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    try:
        if conf.link_type == 1:
            os.symlink(filepath, path + '/' + number + part + c_word + houzhui)
        elif conf.link_type == 2:
            hardlink_force(filepath, path + '/' + number + part + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + part + c_word + houzhui)
        for match in ext_type:
            if os.path.exists(number + match):
                os.rename(number + part + c_word + match, path + '/' + number + part + c_word + match)
                wlogger.info('[+]Sub moved!')
        wlogger.info('[!]Success')
    except FileExistsError:
        wlogger.info('[-]File Exists! Please check your movie!')
        wlogger.info('[-]move to the root folder of the program.')
        return
    except PermissionError:
        wlogger.info('[-]Error! Please run as administrator!')
        return


def get_part(filepath, failed_folder):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        wlogger.info("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return


def core_main(file_path, scrapingnum, cnsubtag, conf: _ScrapingConfigs):
    """
    开始刮削

    番号
    --爬取数据
    --中文/无码等额外信息
    --下载封面--下载预告--下载剧照
    --裁剪图片--增加水印
    --生成nfo--移动视频/字幕

    """
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    c_word = ''
    chs_tag = False
    liuchu = ''

    # 影片的路径 绝对路径
    filepath = file_path
    number = scrapingnum
    json_data = get_data_from_json(number, conf)  # 定义番号

    # Return if blank dict returned (data not found)
    if not json_data:
        wlogger.info('[-]Movie Data not found!')
        if conf.main_mode == 1 and (conf.link_type == 1 or conf.link_type == 2):
            moveFailedFolder(filepath, conf.failed_folder)
        return False, ''

    if json_data.get("number") != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data.get("number")
    imagecut = json_data.get('imagecut')
    tag = json_data.get('tag')
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf.failed_folder)

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
        uncensored = 1
    else:
        uncensored = 0

    # TODO:根据路径判定是否合理
    if '流出' in filepath or '-leak' in filepath:
        liuchu = '流出'
        leak = 1
    else:
        leak = 0

    # main_mode
    #  1: 创建链接刮削 / Scraping mode
    #       - 软链接    - 硬链接    - 移动文件
    #  2: 整理模式 / Organizing mode
    #  3：直接刮削
    if conf.main_mode == 1:
        # 创建文件夹
        path = create_folder(conf.success_folder, json_data.get('location_rule'), json_data, conf)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data.get('cover_small'), c_word, conf, filepath, conf.failed_folder)

        # creatFolder会返回番号路径
        image_download(json_data.get('cover'), number, c_word, path, conf, filepath, conf.failed_folder)
        # 裁剪图
        cutImage(imagecut, path, number, c_word)

        if conf.watermark_enable:
            poster_path = path + '/' + number + c_word + '-poster.jpg'
            thumb_path = path + '/' + number + c_word + '-thumb.jpg'
            add_mark(poster_path, thumb_path, chs_tag, leak, uncensored, conf)

        # 打印文件
        print_files(path, c_word,  json_data.get('naming_rule'), part, chs_tag, json_data, filepath, conf.failed_folder, tag,  json_data.get('actor_list'), liuchu, uncensored)

        # 移动文件
        (flag, path) = paste_file_to_folder(filepath, path, number, c_word, conf)
        return flag, path
    elif conf.main_mode == 2:
        # 创建文件夹
        path = create_folder(conf.success_folder, json_data.get('location_rule'), json_data, conf)
        # 移动文件
        paste_file_to_folder_mode2(filepath, path, multi_part, number, part, c_word, conf)
    elif conf.main_mode == 3:
        path = os.path.dirname(filepath)
        name = os.path.basename(filepath)
        # TODO:直接刮削，传参混乱
        # 临时修改，解决命名不一致问题
        number  = os.path.splitext(name)[0]
        c_word = ''

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data.get('cover_small'), c_word, conf, filepath, conf.failed_folder)

        # creatFolder会返回番号路径
        image_download(json_data.get('cover'), number, c_word, path, conf, filepath, conf.failed_folder)
        # 裁剪图
        cutImage(imagecut, path, number, c_word)

        # 打印文件
        print_files(path, c_word,  json_data.get('naming_rule'), part, chs_tag, json_data, filepath, conf.failed_folder, tag,  json_data.get('actor_list'), liuchu, uncensored)
        
        if conf.watermark_enable:
            poster_path = path + '/' + number + c_word + '-poster.jpg'
            thumb_path = path + '/' + number + c_word + '-thumb.jpg'
            add_mark(poster_path, thumb_path, chs_tag, leak, uncensored, conf)
        return True, file_path
    return False, ''
