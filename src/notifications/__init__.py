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

notificationService = Notification()
