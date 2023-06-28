# -*- coding: utf-8 -*-

import time
import os.path
from collections import deque
from . import wsocket

NUM_LINES = 1000
HEARTBEAT_INTERVAL = 15


@wsocket.route('/ws/logstream')
def logstream(websocket):

    try:
        localPath = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(localPath, "..", "..", "data", "web.log")

        if not os.path.isfile(log_path):
            raise ValueError('Not found log')

        with open(log_path, encoding='utf8') as f:
            content = ''.join(deque(f, NUM_LINES))
            websocket.send(content)
            while True:
                content = f.read()
                if content:
                    websocket.send(content)
                else:
                    time.sleep(10)
    except Exception as e:
        websocket.close()
