# -*- coding: utf-8 -*-
''' 刮削配置
'''
from ..model.config import _ScrapingConfigs, _TransferConfigs
from .. import db


class ScrapingConfService():

    def getSetting(self):
        setting = _ScrapingConfigs.query.filter_by(id=1).first()
        if not setting:
            setting = _ScrapingConfigs()
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


class TransConfService():
    """ 转移模块服务
    """

    def getConfiglist(self):
        configs = _TransferConfigs.query.all()
        return configs

    def getConfig(self):
        config = _TransferConfigs.query.filter_by(id=1).first()
        if not config:
            config = _TransferConfigs()
            db.session.add(config)
            db.session.commit()
        return config

    def updateConf(self, content):
        cid = -1
        if 'id' in content and content['id'] != '':
            cid = content['id']
        config = _TransferConfigs.query.filter_by(id=cid).first()
        if not config:
            config = _TransferConfigs()
            db.session.add(config)
        config.source_folder = content['source_folder']
        config.linktype = content['linktype']
        config.soft_prefix = content['soft_prefix']
        config.output_folder = content['output_folder']
        config.escape_folder = content['escape_folder']
        config.mark = content['mark']
        db.session.commit()
        return config

    def deleteConf(self, cid):
        config = _TransferConfigs.query.filter_by(id=cid).first()
        if config:
            db.session.delete(config)
            db.session.commit()

scrapingConfService = ScrapingConfService()
transConfigService = TransConfService()
