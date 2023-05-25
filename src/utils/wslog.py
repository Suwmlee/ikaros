import time
import os.path
import asyncio
import threading
from collections import deque
from urllib.parse import urlparse, parse_qs
import websockets

NUM_LINES = 1000
HEARTBEAT_INTERVAL = 15


async def view_log(websocket, path):

    try:
        try:
            parse_result = urlparse(path)
        except Exception:
            raise ValueError('Fail to parse URL')

        query = parse_qs(parse_result.query)
        tail = query and query['tail'] and query['tail'][0] == '1'

        if tail:

            localPath = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(localPath, "..", "..", "data", "web.log")

            if not os.path.isfile(log_path):
                raise ValueError('Not found log')

            with open(log_path, encoding='utf8') as f:
                content = ''.join(deque(f, NUM_LINES))
                await websocket.send(content)
                last_heartbeat = time.time()
                while True:
                    content = f.read()
                    if content:
                        await websocket.send(content)
                    else:
                        await asyncio.sleep(1)

                    if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
                        pong = ''
                        await websocket.send('ping')
                        pong = await asyncio.wait_for(websocket.recv(), 5)

                        if pong != 'pong':
                            raise Exception('ping error')
                        last_heartbeat = time.time()
        else:
            await websocket.close()
    except Exception as e:
        try:
            await websocket.close()
        except:
            pass


async def serve(host: str, port: int):
    async with websockets.serve(view_log, host, port):
        await asyncio.Future()


def between_callback(host, port):
    try:
        asyncio.run(serve(host, port))
    except:
        pass


def start_wslogserver(host, port):

    _thread = threading.Thread(target=between_callback, args=(host, port))
    _thread.start()
