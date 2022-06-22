
import os
import transmission_rpc

class Transmission():

    trsession = None

    protocol = 'http'
    host = None
    port = None
    username = None
    password = None

    tags = ["id", "name", "status", "error", "errorString"]

    def __init__(self, url: str, username, password):
        pis = url.split(':')
        pp = pis[len(pis)-1]
        if pp.strip('/').isdigit():
            self.port = pp.strip('/')
            pis.remove(pp)
        if url.startswith('http'):
            self.protocol = pis[0]
            pis.remove(pis[0])
        self.host = ''.join(pis).strip('/')
        if not self.port and self.protocol == 'https':
                self.port = 443
        self.username = username
        self.password = password


    def login(self):
        try:
            trsession = transmission_rpc.Client(host=self.host,
                                                port=self.port,
                                                protocol=self.protocol,
                                                username=self.username,
                                                password=self.password,
                                                timeout=10)
            return trsession
        except Exception as ex:
            print(ex)
            return None

    def getTorrents(self, ids=None, tag=None):
        """ 按条件读取种子信息
        :param ids: ID列表,为空则读取所有
        :param tag: 标签
        """
        if not self.trsession:
            return []
        if isinstance(ids, list):
            ids = [int(x) for x in ids]
        elif ids:
            ids = int(ids)
        torrents = self.trsession.get_torrents(ids=ids, arguments=self.tags)
        return torrents

    def searchByName(self, name):
        torrents = self.getTorrents()
        for i in torrents:
            if i.name == name:
                return i
        return None

    def searchByPath(self, path):
        retry = 3
        for i in range(retry):
            name = os.path.basename(path)
            tt = self.searchByName(name)
            if tt:
                return tt
            else:
                path = os.path.dirname(path)
        return None

    def getTorrentFiles(self, id):
        if not self.trsession:
            return None
        torrent = self.trsession.get_torrent(id)
        if torrent:
            return torrent.files()
        else:
            return None

    def removeTorrent(self, id):
        if not self.trsession:
            return None
        self.trsession.remove_torrent([id])
