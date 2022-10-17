# -*- coding: utf-8 -*-
''' 刮削配置
'''
from ..model.config import _ScrapingConfigs, _TransferConfigs, _AutoConfigs, _LocalConfigs
from .. import db


class ScrapingConfService():

    def getConfiglist(self):
        configs = _ScrapingConfigs.query.all()
        if not configs:
            config = _ScrapingConfigs()
            db.session.add(config)
            db.session.commit()
            configs = []
            configs.append(config)
            return configs
        return configs

    def getConfig(self, sid):
        config = _ScrapingConfigs.query.filter_by(id=sid).first()
        if not config:
            configs = _ScrapingConfigs.query.all()
            if not configs:
                config = _ScrapingConfigs()
                db.session.add(config)
                db.session.commit()
        return config

    def updateConfig(self, content):
        cid = None
        if 'id' in content and content['id']:
            cid = content['id']
        config = _ScrapingConfigs.query.filter_by(id=cid).first()
        if not config:
            config = _ScrapingConfigs()
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
        config = _ScrapingConfigs.query.filter_by(id=cid).first()
        if config:
            db.session.delete(config)
            db.session.commit()


class TransConfService():
    """ 转移模块服务
    """

    def getConfigById(self, cid) -> _TransferConfigs:
        config = _TransferConfigs.query.filter_by(id=cid).first()
        return config

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

    def __init__(self, enable, address, timeout=5, retry=3, proxytype='socks5') -> None:
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


class AutoConfService():
    """ 自动化配置
    """
    def getConfig(self):
        config = _AutoConfigs.query.filter_by(id=1).first()
        if not config:
            config = _AutoConfigs()
            db.session.add(config)
            db.session.commit()
        return config

    def updateConfig(self, content):
        changed = False
        config = self.getConfig()
        for singlekey in content.keys():
            if hasattr(config, singlekey):
                value = getattr(config, singlekey)
                newvalue = content.get(singlekey)
                if value != newvalue:
                    setattr(config, singlekey, newvalue)
                    changed = True
        if changed:
            db.session.commit()
        return True


class LocalConfService():
    """ 通知推送配置
    """
    def getConfig(self):
        config = _LocalConfigs.query.filter_by(id=1).first()
        if not config:
            config = _LocalConfigs()
            db.session.add(config)
            db.session.commit()
        return config

    def updateLoglvl(self, lvl):
        config = self.getConfig()
        config.loglevel = lvl
        db.session.commit()

    def updateConfig(self, content):
        changed = False
        config = self.getConfig()
        for singlekey in content.keys():
            if hasattr(config, singlekey):
                value = getattr(config, singlekey)
                newvalue = content.get(singlekey)
                if value != newvalue:
                    setattr(config, singlekey, newvalue)
                    changed = True
        if changed:
            db.session.commit()
        return True

    def getProxyConfig(self):
        config = _LocalConfigs.query.filter_by(id=1).first()
        proxyConfig = ProxyConfig(config.proxy_enable, config.proxy_address, proxytype=config.proxy_type)
        return proxyConfig


scrapingConfService = ScrapingConfService()
transConfigService = TransConfService()
autoConfigService = AutoConfService()
localConfService = LocalConfService()
