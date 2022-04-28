# -*- coding: utf-8 -*-

from .telegram import Telegram
from .wechat import WeChat

class Notification():

    telegram = None
    wechat = None

    def __init__(self) -> None:
        self.telegram = Telegram()
        self.wechat = WeChat()

    def sendtext(self, text:str):
        self.telegram.sendtext(text)
        self.wechat.sendtext(text)

    def sendWeNews(self, title, description, picurl, url):
        self.wechat.sendnews(title, description, picurl, url)

    def sendWeMarkdown(self, text):
        self.wechat.sendmarkdown(text)

    def sendTgphoto(self, text:str, picpath):
        self.telegram.sendphoto(text, picpath)

    def sendTgMarkdown(self, text):
        self.telegram.sendmarkdown(text)


notificationService = Notification()
