# -*- coding: utf-8 -*-
'''
'''
import os
from .manager import movie_lists
from .info import transferService



def transfer(src_folder, dest_folder, prefix, escape_folders):

    movie_list = movie_lists(src_folder, escape_folders)
    
    for movie_path in movie_list:
        movie_info = transferService.getTransferLogByPath(movie_path)
        if not movie_info or not movie_info.success:
            transferService.addTransferLog(movie_path)

            (filefolder, name) = os.path.split(movie_path)
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            newpath = os.path.join(dest_folder, midfolder, name)
            soft_path = os.path.join(prefix, name)
            # os.symlink(soft_path, newpath)

            transferService.updateTransferLog(movie_path, soft_path, newpath)


    return True
