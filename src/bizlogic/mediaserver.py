# -*- coding: utf-8 -*-
'''
'''
import requests

def refreshMediaServer(url):
    try:
        requests.post(url)
    except:
        pass
