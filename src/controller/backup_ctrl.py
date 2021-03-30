# -*- coding: utf-8 -*-

import os
import xlwt

from flask import request, Response, send_from_directory

from . import web
from ..service.recordservice import scrapingrecordService
from ..utils.wlogger import wlogger


@web.route("/api/export", methods=['GET'])
def export_excel():
    """ 导出JAV excel
    https://skysec.top/2017/07/18/flask%E7%9A%84excel%E5%AF%BC%E5%85%A5%E4%B8%8E%E5%AF%BC%E5%87%BA/
    filename = xlwt.Workbook() 创建一个excel文件
    sheet = filename.add_sheet("my_sheet") 在excel文件里给表单命名
    sheet.write(rows, cols ,content) 在你加入的表单内写入内容,注意参数为行，列，内容
    """
    try:
        directory = os.getcwd()
        filename = "javrecords.xls"
        filefolder = directory + '/database/'
        if os.path.exists(filefolder + filename):
            os.remove(filefolder + filename)
        records = scrapingrecordService.queryAll()
        xlsfile = xlwt.Workbook(encoding='utf-8')
        sheet = xlsfile.add_sheet("Sheet1")
        sheet.write(0, 0, 'srcname')
        sheet.write(0, 1, 'srcpath')
        sheet.write(0, 2, 'srcsize')
        sheet.write(0, 3, 'status')
        for rownum in range(len(records)):
            record = records[rownum]
            sheet.write(rownum+1, 0, record.srcname)
            sheet.write(rownum+1, 1, record.srcpath)
            sheet.write(rownum+1, 2, record.srcsize)
            sheet.write(rownum+1, 3, record.status)

        xlsfile.save(filefolder + filename)
        return send_from_directory(filefolder, filename, as_attachment=True)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)

