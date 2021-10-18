# -*- coding: utf-8 -*-

import os
import xlwt
import xlrd
import datetime

from flask import request, Response, send_from_directory

from . import web
from ..service.recordservice import scrapingrecordService
from ..model.record import _ScrapingRecords
from flask import current_app
from ..utils.filehelper import cleanbySuffix


@web.route("/api/export", methods=['GET'])
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
    参数:file：Excel文件路径    
    colnameindex：表头列名所在行的索引 
    by_index：表的索引
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


@web.route("/api/import", methods=['POST'])
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
                        print("[Backup] Pass: " + srcpath)
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
                        print("[Backup] Add: " + srcpath)
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


@web.route("/api/cleandb", methods=['GET'])
def cleanErrData():
    """ clean record file not exist
    """
    try:
        records = scrapingrecordService.queryAll()
        for i in records:
            srcpath = i.srcpath
            dstpath = i.destpath
            if not os.path.exists(srcpath):
                if i.linktype == 1:
                    print("[Clean scrapingrecord] : " + srcpath)
                    scrapingrecordService.deleteByID(i.id)
                if not os.path.exists(dstpath):
                    print("[Clean scrapingrecord] : " + srcpath)
                    scrapingrecordService.deleteByID(i.id)
        return Response(status=200)
    except Exception as err:
        current_app.logger.error(err)
        return Response(status=500)
