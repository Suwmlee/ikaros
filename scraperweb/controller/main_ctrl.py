
import json
import os
import datetime
from time import sleep
from threading import Lock
from flask import render_template, request, Response

from . import web
from ..bizlogic import manager
from ..bizlogic import transfer
from ..bizlogic.setting import settingService
from ..utils.wlogger import wlogger
from concurrent.futures import ThreadPoolExecutor

# DOCS https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
executor = ThreadPoolExecutor(2)


@web.route("/api/start", methods=['POST'])
def start_scraper():
    try:
        # executor.submit(manager.start)
        manager.start()
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/startscan", methods=['POST'])
def start_scan():
    try:
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)


@web.route("/api/transfer", methods=['POST'])
def start_transfer():
    try:
        content = request.get_json()
        transfer.transfer(content['source_folder'], content['output_folder'], content['soft_prefix'], content['escape_folder'])
        return Response(status=200)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)
