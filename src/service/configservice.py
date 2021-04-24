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
        for singlekey in content.keys():
            if hasattr(setting, singlekey):
                value = getattr(setting, singlekey)
                newvalue = content.get(singlekey)
                if value != newvalue:
                    setattr(setting, singlekey, newvalue)
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
        if not configs:
            config = _TransferConfigs()
            db.session.add(config)
            db.session.commit()
            configs = []
            configs.append(config)
            return configs
        return configs

    def getConfig(self):
        config = _TransferConfigs.query.filter_by(id=1).first()
        if not config:
            config = _TransferConfigs()
            db.session.add(config)
            db.session.commit()
        return config

    def updateConf(self, content):
        cid = None
        if 'id' in content and content['id']:
            cid = content['id']
        config = _TransferConfigs.query.filter_by(id=cid).first()
        if not config:
            config = _TransferConfigs()
            db.session.add(config)
        for singlekey in content.keys():
            if hasattr(config, singlekey) and singlekey != 'id':
                value = getattr(config, singlekey)
                newvalue = content.get(singlekey)
                if value != newvalue:
                    setattr(config, singlekey, newvalue)
        db.session.commit()
        return config

    def deleteConf(self, cid):
        config = _TransferConfigs.query.filter_by(id=cid).first()
        if config:
            db.session.delete(config)
            db.session.commit()

scrapingConfService = ScrapingConfService()
transConfigService = TransConfService()
