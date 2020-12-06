
# -*- coding: utf-8 -*-
''' 刮削配置
'''
from ..model.setting import _Settings
from .. import db


class SettingService():

    setting = None

    def getSetting(self):
        self.setting = _Settings.query.filter_by(id=1).first()
        if not self.setting:
            self.setting = _Settings()
            db.session.add(self.setting)
            db.session.commit()
        return self.setting

    def updateScrapeFolder(self, folder):
        if self.getSetting().scrape_folder != folder:
            self.getSetting().scrape_folder = folder
            db.session.commit()
        return True

    def getProxySetting(self):
        switch = self.getSetting().proxy_enable
        proxytype = self.getSetting().proxy_type
        address = self.getSetting().proxy_address
        timeout = self.getSetting().proxy_timeout
        retry_count = self.getSetting().proxy_retry
        return switch, address, timeout, retry_count, proxytype


settingService = SettingService()
