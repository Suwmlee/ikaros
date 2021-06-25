# -*- coding: utf-8 -*-
'''
'''
import os
import stat
import re
import shutil

from .manager import movie_lists
from .rename import renamebyreg
from ..service.recordservice import transrecordService
from ..service.taskservice import taskService
from ..utils.filehelper import video_type, ext_type, cleanfilebysuffix, cleanfolderwithoutsuffix, hardlink_force, symlink_force
from ..utils.wlogger import wlogger


def copysub(src_folder, destfolder, filter):
    """ copy subtitle
    """
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type and filter in item:
            src_file = os.path.join(src_folder, item)
            print("[-] - copy sub  " + src_file)
            dest = shutil.copy(src_file, destfolder)
            # modify permission
            os.chmod(dest, stat.S_IRWXU | stat.S_IRGRP |
                     stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)


def transfer(src_folder, dest_folder, linktype, prefix, escape_folders, renameflag=False, renameprefix='S01E'):

    task = taskService.getTask('transfer')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'transfer')

    try:
        movie_list = movie_lists(src_folder, re.split("[,，]", escape_folders))

        count = 0
        total = str(len(movie_list))
        taskService.updateTaskTotal(total, 'transfer')
        print('[+]Find  ' + total+'  movies')

        # 硬链接直接使用源目录
        if linktype == 1:
            prefix = src_folder
        # 清理目标目录下的文件：视频 字幕
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        clean_type = video_type + ext_type
        cleanfilebysuffix(dest_folder, clean_type)

        for movie_path in movie_list:
            count += 1
            taskService.updateTaskFinished(count, 'transfer')
            print('[!] - ' + str(count) + '/' + total + ' -')
            print("[+] start check [{}] ".format(movie_path))
            movie_info = transrecordService.queryByPath(movie_path)
            if not movie_info:
                movie_info = transrecordService.add(movie_path)

            (filefolder, name) = os.path.split(movie_path)
            midfolder = filefolder.replace(
                src_folder, '').lstrip("\\").lstrip("/")
            # 目的地址
            newpath = os.path.join(dest_folder, midfolder, name)
            # 链接的源地址
            link_path = os.path.join(prefix, midfolder, name)

            if os.path.exists(newpath):
                realpath = os.path.realpath(newpath)
                if realpath == link_path:
                    print("[!] already exists")
                    transrecordService.update(movie_path, link_path, newpath)
                    continue
                else:
                    print("[-] clean link")
                    os.remove(newpath)
            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)

            print("[-] create link from [{}] to [{}]".format(link_path, newpath))
            if linktype == 0:
                symlink_force(link_path, newpath)
            else:
                hardlink_force(link_path, newpath)
            basename = os.path.splitext(name)[0]
            copysub(filefolder, newfolder, basename)
            print("[-] transfer finished [{}]".format(movie_path))
            transrecordService.update(movie_path, link_path, newpath)

        cleanfolderwithoutsuffix(dest_folder, video_type)
        # 重命名
        if renameflag:
            reg = '[\[第 ][0-9.svidevoa\(\)]*[\]話话 ]'
            reg2 = "\.e[0-9videvoa\(\)]{1,}[.]"
            renamebyreg(dest_folder, reg, reg2, renameprefix, False)

        print("transfer finished")
    except:
        import traceback
        err = traceback.format_exc()
        wlogger.error(err)

    taskService.updateTaskStatus(1, 'transfer')

    return True
