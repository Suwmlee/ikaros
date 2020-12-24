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
        if 'proxy_enable' in content and setting.proxy_enable != content['proxy_enable']:
            setting.proxy_enable = content['proxy_enable']
            changed = True
        if 'proxy_type' in content and setting.proxy_type != content['proxy_type']:
            setting.proxy_type = content['proxy_type']
            changed = True
        if 'proxy_address' in content and setting.proxy_address != content['proxy_address']:
            setting.proxy_address = content['proxy_address']
            changed = True
        if changed:
            db.session.commit()
        return True

    def getProxySetting(self):
        setting = self.getSetting()
        switch = setting.proxy_enable
        proxytype = setting.proxy_type
        address = setting.proxy_address
        timeout = setting.proxy_timeout
        retry_count = setting.proxy_retry
        return switch, address, timeout, retry_count, proxytype


settingService = SettingService()
