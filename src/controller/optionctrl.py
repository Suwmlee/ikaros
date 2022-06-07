# -*- coding: utf-8 -*-

import os
import json
import logging
import xlwt
import xlrd
import datetime
import time

from flask import request, Response, send_from_directory

from . import web
from ..model.record import _ScrapingRecords
from flask import current_app
from ..utils.filehelper import cleanbySuffix
from ..service.recordservice import scrapingrecordService, transrecordService
from ..service.configservice import notificationConfService

@web.route("/api/options/loglevel", methods=['GET', 'PUT'])
def loglevel():
    """
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
    """
    try:
        if request.method == 'GET':
            level = current_app.logger.level
            ret = {'loglevel': level}
            return json.dumps(ret)
        if request.method == 'PUT':
            content = request.get_json()
            if content and 'loglevel' in content:
                level = int(content.get('loglevel'))
                current_app.logger.setLevel(level)
            else:
                current_app.logger.setLevel(logging.INFO)
            return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/options/exportjav", methods=['GET'])
def exportExcel():
    """ 导出JAV excel
    https://skysec.top/2017/07/18/flask%E7%9A%84excel%E5%AF%BC%E5%85%A5%E4%B8%8E%E5%AF%BC%E5%87%BA/
    filename = xlwt.Workbook() 创建一个excel文件
    sheet = filename.add_sheet("my_sheet") 在excel文件里给表单命名
    sheet.write(rows, cols ,content) 在你加入的表单内写入内容,注意参数为行，列，内容
    """
    try:
        directory = os.getcwd()
        nowtime = datetime.datetime.now()
        filename = "records-"+nowtime.strftime("%H%M%S-%m%d%Y")+".xls"
        filefolder = directory + '/database/'
        cleanbySuffix(filefolder, ['.xls', '.xlsx'])
        records = scrapingrecordService.queryAll()

        temp = _ScrapingRecords('','')
        temp.updatetime = nowtime
        headers = temp.serialize()

        xlsfile = xlwt.Workbook(encoding='utf-8')
        sheet = xlsfile.add_sheet("Sheet1")
        header_keys = list(headers.keys())

        i = 0
        for header in header_keys:
            sheet.write(0, i, header)
            i = i + 1
        for rownum in range(len(records)):
            record = records[rownum]
            j = 0
            for header in header_keys:
                value = getattr(record, header)
                sheet.write(rownum + 1, j, value)
                j = j + 1

        xlsfile.save(filefolder + filename)
        return send_from_directory(filefolder, filename, as_attachment=True, cache_timeout=0)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


def openExcel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file, encoding_override="utf-8")
        return data
    except Exception as e:
        current_app.logger.error(e)


def allowedFormat(file='file.xls', colnameindex=0, by_index=0):
    """
    根据索引获取Excel表格中的数据   
    参数:file       Excel文件路径    
    colnameindex:   表头列名所在行的索引 
    by_index:       表的索引
    """
    data = openExcel(file)
    table = data.sheets()[by_index]
    colnames = table.row_values(colnameindex)
    if colnames[0] == "srcname" and \
            colnames[1] == "srcpath" and \
            colnames[2] == "srcsize" and \
            colnames[3] == "status":
        return 1
    else:
        return 0


ALLOWED_EXTENSIONS = ['xls', 'xlsx']


def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@web.route("/api/options/importjav", methods=['POST'])
def importExcel():
    """ 导入JAV excel
    """
    try:
        file = request.files['file']
        filename = file.filename

        if file and allowedFile(filename):
            file.save('import' + filename)
            data = openExcel(file='import' + filename).sheets()[0]
            nrows = data.nrows
            pass_num = 0
            success_num = 0
            headers = data.row_values(0)
            if "srcpath" in headers:
                for i in range(1, nrows):
                    srcpath = data.row_values(i)[headers.index('srcpath')]
                    u = scrapingrecordService.queryByPath(srcpath)
                    if u:
                        pass_num += 1
                        current_app.logger.debug("[Backup] Pass: " + srcpath)
                    else:
                        t = scrapingrecordService.add(srcpath)
                        for singlekey in headers:
                            if hasattr(t, singlekey) and singlekey != 'id':
                                if singlekey == 'updatetime':
                                    t.updatetime = datetime.datetime.now()
                                else:
                                    newvalue = data.row_values(i)[headers.index(singlekey)]
                                    setattr(t, singlekey, newvalue)
                        scrapingrecordService.commit()
                        success_num += 1
                        current_app.logger.debug("[Backup] Add: " + srcpath)
                os.remove('import' + filename)
                return Response(status=200)
            else:
                os.remove('import' + filename)
                return Response(status=500)
        else:
            return Response(status=403)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)


@web.route("/api/options/cleanrecord", methods=['GET'])
def cleanErrData():
    """ clean record file not exist
    """
    try:
        scrapingrecordService.cleanUnavailable()
        transrecordService.cleanUnavailable()
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)

# TODO refactor log

def flask_logger():
    """creates logging information"""
    localPath = os.path.dirname(os.path.abspath(__file__))
    # TODO get web.log
    logfile = os.path.join(localPath, "..", "..", "database", "web.log")
    with open(logfile, encoding='UTF-8') as log_info:
        for i in range(25):
            data = log_info.read()
            yield data.encode()
            time.sleep(1)


@web.route("/api/options/logstream", methods=["GET"])
def stream():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream; charset=utf-8")


@web.route("/api/options/notification", methods=["GET"])
def getNotificationConfig():
    """returns notification config"""
    try:
        content = notificationConfService.getConfig().serialize()
        return json.dumps(content)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)

@web.route("/api/options/notification", methods=['PUT'])
def updateNotifiConf():
    try:
        content = request.get_json()
        notificationConfService.updateConfig(content)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
