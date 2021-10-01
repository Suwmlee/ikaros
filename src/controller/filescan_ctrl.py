# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from flask import url_for, request
from . import web
from ..utils.log import log


@web.route('/api/scan/', methods=['POST'])
def direcotry():
    try:
        content = request.get_json()
        if content.get('path'):
            media_dir = content.get('path')
        else:
            media_dir = '/'
        log.debug(media_dir)
        parentdir = os.path.dirname(media_dir)
        ret = dict()
        ret['parent'] = parentdir
        dir_ele_list = list()
        for f in (Path('/') / Path(media_dir)).iterdir():
            fullname = str(f).replace('\\', '/')
            if f.is_dir():
                fullname = str(f).replace('\\', '/')
                dir_ele_list.append({'is_dir': 1, 'filesize': 0,
                                    'url': url_for('web.direcotry', media_dir=fullname[0:]),
                                    'fullname': fullname})
        ret['dirs'] = dir_ele_list
        return json.dumps(ret)
    except PermissionError:
        ret = {'error': '拒绝访问'}
        return json.dumps(ret)
    except Exception as e:
        log.error(e)
        ret = {'error': str(e)}
        return json.dumps(ret)
