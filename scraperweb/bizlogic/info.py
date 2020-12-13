# -*- coding: utf-8 -*-
'''
'''
import os
import datetime
from ..model.info import _Info
from .. import db


class InfoService():

    def addInfo(self, path):
        info = self.getInfoByPath(path)
        if not info:
            (filefolder, name) = os.path.split(path)
            info = _Info(name, path)
            db.session.add(info)
            db.session.commit()
            return info
        return info

    def getInfoByPath(self, value):
        info = _Info.query.filter_by(basepath=value).first()
        if not info:
            return None
        return info

    def updateInfo(self, path, newname):
        info = self.getInfoByPath(path)
        if info:
            info.newname = newname
            info.success = True
            info.updatetime = datetime.datetime.now()
            db.session.commit()

infoService = InfoService()
