# -*- coding: utf-8 -*-
'''
'''
import os
import errno
import shutil
from .manager import movie_lists
from ..service.info import transferService
from ..utils.filehelper import video_type, video_filter, cleanfilebysuffix, cleanfolderwithoutsuffix


def copysub(src_folder, destfolder):
    """ copy subtitle
    """
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in video_type:
            src_file = os.path.join(src_folder, item)
            print("copy sub" + src_file)
            shutil.copy(src_file, destfolder)


def symlink_force(target, link_name):
    """ create symlink
    https://stackoverflow.com/questions/8299386/modifying-a-symlink-in-python
    """
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def transfer(src_folder, dest_folder, prefix, escape_folders):

    movie_list = movie_lists(src_folder, escape_folders)

    cleanfilebysuffix(dest_folder, video_type)

    for movie_path in movie_list:
        print("start check [{}] ".format(movie_path))
        movie_info = transferService.getTransferLogByPath(movie_path)
        if not movie_info:
            movie_info = transferService.addTransferLog(movie_path)

        (filefolder, name) = os.path.split(movie_path)
        midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
        newpath = os.path.join(dest_folder, midfolder, name)
        soft_path = os.path.join(prefix, midfolder, name)

        if os.path.exists(newpath):
            realpath = os.path.realpath(newpath)
            if realpath == soft_path:
                print("already exists")
                transferService.updateTransferLog(movie_path, soft_path, newpath)
                continue
            else:
                print("clean soft link")
                os.remove(newpath)
        (newfolder, tname) = os.path.split(newpath)
        if not os.path.exists(newfolder):
            os.makedirs(newfolder)
        print("create soft link from [{}] to [{}]".format(soft_path, newpath))
        symlink_force(soft_path, newpath)
        copysub(filefolder, newfolder)
        print("transfer Data for [{}], the number is [{}]".format(movie_path, newpath))
        transferService.updateTransferLog(movie_path, soft_path, newpath)

    cleanfolderwithoutsuffix(dest_folder, video_type)

    print("transfer finished")
    return True
