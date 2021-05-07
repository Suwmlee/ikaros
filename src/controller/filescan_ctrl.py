# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path

from flask import url_for
from . import web


@web.route('/api/scan/', )
@web.route('/api/scan/<path:media_dir>', )
def direcotry(media_dir=''):
    # current_app.logger.debug(media_dir)
    dir_ele_list = list()
    for f in (Path('/') / Path(media_dir)).iterdir():
        fullname = str(f).replace('\\', '/')
        if f.is_dir():
            fullname = str(f).replace('\\', '/')
            dir_ele_list.append({'is_dir': 1, 'filesize': 0,
                                 'url': url_for('web.direcotry', media_dir=fullname[0:]),
                                 'fullname': fullname})

    return json.dumps(dir_ele_list)
