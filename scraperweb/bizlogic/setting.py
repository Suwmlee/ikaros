# -*- coding: utf-8 -*-
''' 刮削配置
'''
from ..model.setting import _Settings
from .. import db


class SettingService():

    def getSetting(self):
        setting = _Settings.query.filter_by(id=1).first()
        if not setting:
            setting = _Settings()
            db.session.add(setting)
            db.session.commit()
        return setting

    def updateSetting(self, content):
        changed = False
        setting = self.getSetting()
        if 'scrape_folder' in content and setting.scrape_folder != content['scrape_folder']:
            setting.scrape_folder = content['scrape_folder']
            changed = True
        if 'success_folder' in content and setting.success_folder != content['success_folder']:
            setting.success_folder = content['success_folder']
            changed = True
        if 'location_rule' in content and setting.location_rule != content['location_rule']:
            setting.location_rule = content['location_rule']
            changed = True
        if 'naming_rule' in content and setting.naming_rule != content['naming_rule']:
            setting.naming_rule = content['naming_rule']
            changed = True
        if 'soft_link' in content and setting.soft_link != content['soft_link']:
            setting.soft_link = content['soft_link']
            changed = True
        if 'soft_prefix' in content and setting.soft_prefix != content['soft_prefix']:
            setting.soft_prefix = content['soft_prefix']
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
