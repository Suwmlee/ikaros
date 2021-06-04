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
        proxyConfig = ProxyConfig(setting.proxy_enable, setting.proxy_address,
                                  setting.proxy_timeout, setting.proxy_retry, setting.proxy_type)
        return proxyConfig


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


class ProxyConfig():
    """ Proxy Config
    """
    SUPPORT_PROXY_TYPE = ("http", "socks5", "socks5h")

    enable = False
    address = ""
    timeout = 5
    retry = 3
    proxytype = "socks5"

    def __init__(self, enable, address, timeout, retry, proxytype) -> None:
        """ Initial Proxy
        """
        self.enable = enable
        self.address = address
        self.timeout = timeout
        self.retry = retry
        self.proxytype = proxytype

    def proxies(self):
        ''' 获得代理参数
        '''
        if self.address:
            if self.proxytype in self.SUPPORT_PROXY_TYPE:
                proxies = {"http": self.proxytype + "://" + self.address,
                           "https": self.proxytype + "://" + self.address}
            else:
                proxies = {"http": "http://" + self.address,
                           "https": "https://" + self.address}
        else:
            proxies = {}

        return proxies


scrapingConfService = ScrapingConfService()
transConfigService = TransConfService()
