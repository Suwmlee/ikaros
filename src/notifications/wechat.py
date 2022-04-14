# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from flask import current_app
from ..service.configservice import notificationConfService


class WeChat():

    corpid = None
    corpsecret = None
    agentid = None

    access_token = None
    expires_in = None
    get_token_time = None

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36",
                "content-type": "charset=utf8"}
    timeout = 20

    def updateConfig(self):
        config = notificationConfService.getConfig()
        if config.wechat_corpid and config.wechat_corpsecret and config.wechat_agentid:
            self.corpid = config.wechat_corpid
            self.corpsecret = config.wechat_corpsecret
            self.agentid = config.wechat_agentid
            return True
        return False

    def sendtext(self, text: str):
        """ 使用 企业微信 发送文本消息
        """
        if self.updateConfig():
            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(self.updateAccessToken())
            for i in range(3):
                requestContent = {
                    "touser": "@all",
                    "msgtype": "text",
                    "agentid": self.agentid,
                    "text": {
                        "content": text
                    },
                    "safe": 0,
                    "enable_id_trans": 0,
                    "enable_duplicate_check": 0
                }
                try:
                    result = requests.post(url, json=requestContent, headers= self.headers, timeout= self.timeout)
                    if result:
                        ret = result.json()
                        if ret['errcode'] == 0:
                            current_app.logger.error("[!] 推送: 微信消息 {}".format(ret['errmsg']))
                            break
                except:
                    pass

    def updateAccessToken(self):
        """ 获取 access_token,具有时效性
        """
        have_valid_token = False
        if self.access_token:
            current_time = datetime.now()
            if (current_time - self.get_token_time).seconds < self.expires_in:
                have_valid_token = True

        if not have_valid_token:
            if not self.corpid or not self.corpsecret:
                return None
            try:
                tokenurl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(self.corpid, self.corpsecret)
                response = requests.get(tokenurl, headers= self.headers, timeout= self.timeout)
                if response:
                    ret = response.json()
                    if ret['errcode'] == 0:
                        self.get_token_time = datetime.now()
                        self.access_token = ret['access_token']
                        self.expires_in = ret['expires_in']
                    else:
                        current_app.logger.error("[!] 推送: 微信消息 {}".format(ret['errmsg']))
            except Exception as e:
                current_app.logger.error("[!] 推送:获取微信access_token错误")
                current_app.logger.error(e)
                return None
        return self.access_token
