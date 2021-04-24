# -*- coding: utf-8 -*-

import os
from ..utils.filehelper import video_type, ext_type


def file_lists(root):
    total = []
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.splitext(f)[1] in video_type or os.path.splitext(f)[1] in ext_type:
            total.append(f)
    return total


def rename(root, base, newfix):
    tvs = file_lists(root)
    for name in tvs:
        dirname,basename=os.path.split(name)
        if base in basename:
            newname = basename.replace(base, newfix)
            newfull = os.path.join(dirname, newname)
            os.rename(name, newfull)
            
            print("rename [{}] to [{}]".format(name, newfull))


if __name__ == "__main__":

    root = os.getcwd()
    base= 'People.2017.'
    newfix = 'People.2017.S01' 
    rename(root, base, newfix)
