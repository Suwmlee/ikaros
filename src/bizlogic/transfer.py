# -*- coding: utf-8 -*-
'''
'''
import os
import shutil
from .manager import movie_lists
from ..service.logservice import translogService
from ..service.taskservice import taskService
from ..utils.filehelper import video_type, ext_type, cleanfilebysuffix, cleanfolderwithoutsuffix, hardlink_force, symlink_force
from ..utils.wlogger import wlogger


def copysub(src_folder, destfolder):
    """ copy subtitle
    """
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in ext_type:
            src_file = os.path.join(src_folder, item)
            print("copy sub  " + src_file)
            shutil.copy(src_file, destfolder)


def transfer(src_folder, dest_folder, linktype, prefix, escape_folders):

    task = taskService.getTask('transfer')
    if task.status == 2:
        return
    taskService.updateTaskStatus(2, 'transfer')

    try:
        movie_list = movie_lists(src_folder, escape_folders)

        # 硬链接直接使用源目录
        if linktype == 1:
            prefix = src_folder

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        cleanfilebysuffix(dest_folder, video_type)

        for movie_path in movie_list:
            print("start check [{}] ".format(movie_path))
            movie_info = translogService.getTransferLogByPath(movie_path)
            if not movie_info:
                movie_info = translogService.addTransferLog(movie_path)

            (filefolder, name) = os.path.split(movie_path)
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            newpath = os.path.join(dest_folder, midfolder, name)
            link_path = os.path.join(prefix, midfolder, name)

            if os.path.exists(newpath):
                realpath = os.path.realpath(newpath)
                if realpath == link_path:
                    print("already exists")
                    translogService.updateTransferLog(movie_path, link_path, newpath)
                    continue
                else:
                    print("clean link")
                    os.remove(newpath)
            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            print("create link from [{}] to [{}]".format(link_path, newpath))
            if linktype == 0:
                symlink_force(link_path, newpath)
            else:
                hardlink_force(link_path, newpath)
            copysub(filefolder, newfolder)
            print("transfer Data for [{}], the number is [{}]".format(movie_path, newpath))
            translogService.updateTransferLog(movie_path, link_path, newpath)

        cleanfolderwithoutsuffix(dest_folder, video_type)

        print("transfer finished")
    except:
        import traceback
        err = traceback.format_exc()
        wlogger.error(err)

    taskService.updateTaskStatus(1, 'transfer')

    return True
