# -*- coding: utf-8 -*-

from scrapinglib import httprequest
from flask import current_app
from ..service.configservice import localConfService


class Telegram():

    token = None
    chatid = None

    def updateConfig(self):
        config = localConfService.getConfig()
        if config.tg_chatid and config.tg_token:
            self.token = config.tg_token
            self.chatid = config.tg_chatid
            return True
        return False

    def sendtext(self, text: str):
        """ 使用telegram bot发送文本消息
        """
        if self.updateConfig():
            url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(self.token, self.chatid, text)
            configProxy = localConfService.getProxyConfig()
            proxies = configProxy.proxies() if configProxy.enable else None
            try:
                httprequest.get(url, proxies=proxies)
            except Exception as ex:
                current_app.logger.debug(ex)
                pass

    def sendmarkdown(self, text: str):
        """ 使用telegram bot发送文本消息
        """
        if self.updateConfig():
            params = {'chat_id': self.chatid, 'text': text, 'parse_mode': 'markdown'}
            url = "https://api.telegram.org/bot{}/sendMessage".format(self.token)
            configProxy = localConfService.getProxyConfig()
            proxies = configProxy.proxies() if configProxy.enable else None
            try:
                httprequest.post(url, params, proxies=proxies)
            except Exception as ex:
                current_app.logger.debug(ex)
                pass

    def sendphoto(self, caption: str, photopath):
        """ 使用telegram bot发送文本消息
        """
        if self.updateConfig():
            params = {'chat_id': self.chatid, 'caption': caption, 'parse_mode': 'markdown'}
            with open(photopath, 'rb') as pic:
                files = {'photo': pic}
                url = "https://api.telegram.org/bot{}/sendPhoto".format(self.token)
                configProxy = localConfService.getProxyConfig()
                proxies = configProxy.proxies() if configProxy.enable else None
                try:
                    httprequest.post(url, params, files=files, proxies=proxies)
                except Exception as ex:
                    current_app.logger.debug(ex)
                    pass         
