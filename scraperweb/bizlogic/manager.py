
import argparse
import os
from flask import current_app as app

from .setting import settingService
from .scraper import *
from ..utils.number_parser import get_number



def check_update(local_version):
    data = json.loads(get_html("https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"))

    remote = data["tag_name"]
    local = local_version

    if not local == remote:
        line1 = "* New update " + str(remote) + " *"
        app.logger.info("[*]" + line1.center(54))
        app.logger.info("[*]" + "↓ Download ↓".center(54))
        app.logger.info("[*] https://github.com/yoshiko2/AV_Data_Capture/releases")
        app.logger.info("[*]======================================================")


def argparse_function(ver: str) -> [str, str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number")
    parser.add_argument("--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.config, args.number


def movie_lists(root, escape_folder):
    for folder in escape_folder:
        if folder in root:
            return []
    total = []
    file_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV', '.MOV', '.MKV', '.FLV', '.TS', '.WEBM', '.iso', '.ISO']
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1] in file_type:
            total.append(f)
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            app.logger.info("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)


def CEF(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            app.logger.info('[+]Deleting empty folder', path + '/' + file)
    except:
        a = ''


def create_data_and_move(file_path: str, c, debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    n_number = get_number(debug, file_path)

    if debug == True:
        app.logger.info("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
        core_main(file_path, n_number, c)
        app.logger.info("[*]======================================================")
    else:
        try:
            app.logger.info("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            core_main(file_path, n_number, c)
            app.logger.info("[*]======================================================")
        except Exception as err:
            app.logger.info("[-] [{}] ERROR:".format(file_path))
            app.logger.info(err)

            # 3.7.2 New: Move or not move to failed folder.
            if not c.failed_move:
                if c.soft_link:
                    app.logger.info("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, str(os.getcwd()) + "/" + c.failed_folder + "/")
            elif c.failed_move == True:
                if c.soft_link:
                    app.logger.info("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, str(os.getcwd()) + "/" + c.failed_folder + "/")
                else:
                    try:
                        app.logger.info("[-]Move [{}] to failed folder".format(file_path))
                        shutil.move(file_path, str(os.getcwd()) + "/" + c.failed_folder + "/")
                    except Exception as err:
                        app.logger.info('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, c, custom_number=None):
    try:
        app.logger.info("[!]Making Data for [{}], the number is [{}]".format(file_path, custom_number))
        core_main(file_path, custom_number, c)
        app.logger.info("[*]======================================================")
    except Exception as err:
        app.logger.info("[-] [{}] ERROR:".format(file_path))
        app.logger.info('[-]', err)

        if c.soft_link():
            app.logger.info("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
        else:
            try:
                app.logger.info("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            except Exception as err:
                app.logger.info('[!]', err)


def start():
    version = '4.0.3'

    # Parse command line args
    # single_file_path, config_file, custom_number = argparse_function(version)

    # Read config.ini
    # conf = config._Settings(path=config_file)
    conf = settingService.getSetting()

    version_print = 'Version ' + version
    app.logger.info('[*]================== AV Data Capture ===================')
    app.logger.info('[*]' + version_print.center(54))
    app.logger.info('[*]======================================================')

    if conf.update_check:
        check_update(version)

    create_failed_folder(conf.failed_folder)
    os.chdir(conf.scrape_folder)

    # # ========== Single File ==========
    # if not single_file_path == '':
    #     app.logger.info('[+]==================== Single File =====================')
    #     create_data_and_move_with_custom_number(single_file_path, conf,custom_number)
    #     CEF(conf.success_folder)
    #     CEF(conf.failed_folder)
    #     app.logger.info("[+]All finished!!!")
    #     input("[+][+]Press enter key exit, you can check the error messge before you exit.")
    #     exit()
    # ========== Single File ==========

    movie_list = movie_lists(conf.scrape_folder, re.split("[,，]", conf.escape_folders))

    count = 0
    count_all = str(len(movie_list))
    app.logger.info('[+]Find  ' + count_all+'  movies')
    if conf.debug_info == True:
        app.logger.info('[+]'+' DEBUG MODE ON '.center(54, '-'))
    if conf.soft_link:
        app.logger.info('[!] --- Soft link mode is ENABLE! ----')
    for movie_path in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        app.logger.info('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        create_data_and_move(movie_path, conf, conf.debug_info)

    CEF(conf.success_folder)
    CEF(conf.failed_folder)
    app.logger.info("[+]All finished!!!")
    # if conf.auto_exit:
    #     os._exit(0)
    # input("[+][+]Press enter key exit, you can check the error message before you exit.")
