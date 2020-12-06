
# -*- coding: utf-8 -*-
''' 刮削配置
'''
from ..model.setting import _Settings
from .. import db


class SettingService():

    setting = None

    def getSetting(self):        
        if self.setting:
            return self.setting
        self.setting = _Settings.query.filter_by(id=1).first()
        if not self.setting:
            self.setting = _Settings()
            db.session.add(self.setting)
            db.session.commit()
        return self.setting

    def updateSetting(self, content):
        changed = False
        self.setting = _Settings.query.filter_by(id=1).first()
        if not self.setting:
            self.setting = _Settings()
            db.session.add(self.setting)
            changed = True
        if self.setting.scrape_folder != content['scrape_folder']:
            self.setting.scrape_folder = content['scrape_folder']
            changed = True
        if self.setting.location_rule != content['location_rule']:
            self.setting.location_rule = content['location_rule']
            changed = True
        if self.setting.naming_rule != content['naming_rule']:
            self.setting.naming_rule = content['naming_rule']
            changed = True
        if changed:
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
