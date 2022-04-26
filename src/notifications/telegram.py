# -*- coding: utf-8 -*-
import requests
from ..service.configservice import notificationConfService


class Telegram():

    token = None
    chatid = None

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"}
    timeout = 20

    def updateConfig(self):
        config = notificationConfService.getConfig()
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
            for i in range(3):
                try:
                    result = requests.get(url, headers= self.headers, timeout= self.timeout)
                    if result.status_code == 200:
                        break
                except:
                    pass

    def sendmarkdown(self, text: str):
        """ 使用telegram bot发送文本消息
        """
        if self.updateConfig():
            params = {'chat_id': self.chatid, 'text': text, 'parse_mode': 'markdown'}
            url = "https://api.telegram.org/bot{}/sendMessage".format(self.token)
            for i in range(3):
                try:
                    result = requests.post(url, params, headers= self.headers, timeout= self.timeout)
                    if result.status_code == 200:
                        break
                except:
                    pass

    def sendphoto(self, caption: str, photopath):
        """ 使用telegram bot发送文本消息
        """
        if self.updateConfig():
            params = {'chat_id': self.chatid, 'caption': caption, 'parse_mode': 'markdown'}
            with open(photopath, 'rb') as pic:
                files = {'photo': pic}
                url = "https://api.telegram.org/bot{}/sendPhoto".format(self.token)
                for i in range(3):
                    try:
                        result = requests.post(url, params, headers= self.headers, files=files, timeout= self.timeout)
                        if result.status_code == 200:
                            break
                    except:
                        pass
