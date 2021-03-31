# -*- coding: utf-8 -*-

import os
import xlwt
import xlrd

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


def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file, encoding_override="utf-8")
        return data
    except Exception as e:
        print(str(e))


def allowed_format(file='file.xls', colnameindex=0, by_index=0):
    """
# 根据索引获取Excel表格中的数据   
# 参数:file：Excel文件路径    
# colnameindex：表头列名所在行的索引 
# by_index：表的索引
    """
    data = open_excel(file)
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@web.route("/api/import", methods=['POST'])
def import_excel():
    """ 导入JAV excel
    """
    try:
        file = request.files['file']
        filename = file.filename

        if file and allowed_file(filename):
            file.save('import' + filename)
            flag = allowed_format(file='import' + filename)
            if flag:
                data = open_excel(file='import' + filename).sheets()[0]
                nrows = data.nrows
                pass_num = 0
                success_num = 0
                for i in range(1, nrows):
                    test = data.row_values(i)[1]
                    u = scrapingrecordService.queryByPath(test)
                    if (u):
                        pass_num += 1
                    else:
                        rowname = data.row_values(i)[0]
                        rowpath = data.row_values(i)[1]
                        rowsize = data.row_values(i)[2]
                        rowstatus = data.row_values(i)[3]
                        scrapingrecordService.importRecord(rowname, rowpath, rowsize, rowstatus)
                        success_num += 1
                os.remove('import' + filename)
                return Response(status=200)
            else:
                os.remove('import' + filename)
                return Response(status=500)
        else:
            return Response(status=403)
    except Exception as err:
        wlogger.info(err)
        return Response(status=500)
