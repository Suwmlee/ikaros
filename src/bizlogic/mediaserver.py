# -*- coding: utf-8 -*-
'''
'''
import requests
from flask import current_app

def refreshMediaServer(url):
    try:
        requests.post(url, timeout=5)
        return True
    except Exception as e:
        current_app.logger.error("[!] Refresh Media Err")
        current_app.logger.error(e)
        return False
