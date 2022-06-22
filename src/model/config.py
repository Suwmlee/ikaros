# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean
from .. import db


class _ScrapingConfigs(db.Model):
    """ 
    main_mode:
    :1  移动刮削
        link_type:
        :0  移动文件
        :1  软链接
        :2  硬链接
    :2  整理
    :3  直接刮削
    """
    __tablename__ = 'scrapingconfigs'

    id = Column(Integer, primary_key=True)
    main_mode = Column(Integer, default=1)
    multi_scraping = Column(Boolean, default=False, comment="Multiple file scraping at the same time")
    async_request = Column(Boolean, default=False, comment="Scrape a movie asynchronously")

    scraping_folder = Column(String, default='/media')
    failed_folder = Column(String, default='/media/failed')
    success_folder = Column(String, default='/media/output')
    link_type = Column(Integer, default=1)
    soft_prefix = Column(String, default='/media')
    failed_move = Column(Boolean, default=False)

    proxy_enable = Column(Boolean, default=False)
    proxy_type = Column(String, default='socks5h')
    proxy_address = Column(String, default='127.0.0.1:1080')
    proxy_timeout = Column(Integer, default=10)
    proxy_retry = Column(Integer, default=3)

    site_sources = Column(String, default="")
    location_rule = Column(String, default="actor+'/'+number+' '+title")
    naming_rule = Column(String, default="number+' '+title")
    max_title_len = Column(Integer, default=50)
    update_check = Column(Boolean, default=False)
    morestoryline = Column(Boolean, default=True)

    extrafanart_enable = Column(Boolean, default=False)
    extrafanart_folder = Column(String, default='extrafanart', server_default='extrafanart')
    watermark_enable = Column(Boolean, default=True, comment='enable water mark')
    watermark_size = Column(Integer, default=9)
    watermark_location = Column(Integer, default=2)

    escape_folders = Column(String, default="failed,output")
    escape_literals = Column(String, default="\()/")
    escape_size = Column(Integer, default=0)

    transalte_enable = Column(Boolean, default=False)
    transalte_to_sc = Column(Boolean, default=False)
    transalte_values = Column(String, default="title,outline")

    cookies_javdb = Column(String, default="")
    cookies_javlib = Column(String, default="")
    refresh_url = Column(String, default='')
    remark = Column(String, default='备注')

    def serialize(self):
        return {
            'id': self.id,
            'main_mode': self.main_mode,
            'multi_scraping': self.multi_scraping,
            'async_request': self.async_request,
            'link_type': self.link_type,
            'soft_prefix': self.soft_prefix,
            'scraping_folder': self.scraping_folder,
            'success_folder': self.success_folder,
            'failed_folder': self.failed_folder,
            'location_rule': self.location_rule,
            'naming_rule': self.naming_rule,
            'site_sources': self.site_sources,
            'morestoryline': self.morestoryline,
            'extrafanart_enable': self.extrafanart_enable,
            'extrafanart_folder': self.extrafanart_folder,
            'watermark_enable': self.watermark_enable,
            'watermark_location': self.watermark_location,
            'watermark_size': self.watermark_size,
            'escape_folders': self.escape_folders,
            'escape_size': self.escape_size,
            'proxy_enable': self.proxy_enable,
            'proxy_type': self.proxy_type,
            'proxy_address': self.proxy_address,
            'proxy_timeout': self.proxy_timeout,
            'proxy_retry': self.proxy_retry,
            'cookies_javdb': self.cookies_javdb,
            'cookies_javlib': self.cookies_javlib,
            'refresh_url': self.refresh_url,
            'remark': self.remark
        }


class _TransferConfigs(db.Model):
    __tablename__ = 'transferconfigs'

    id = Column(Integer, primary_key=True)
    source_folder = Column(String, default='/media')
    soft_prefix = Column(String, default='/volume1/Media')
    linktype = Column(Integer, default=0)
    output_folder = Column(String, default='/media/output')
    escape_folder = Column(String, default='Sample,sample')
    escape_size = Column(Integer, default=0)
    clean_others = Column(Boolean, default=False)
    replace_CJK = Column(Boolean, default=False)
    fix_series = Column(Boolean, default=False)
    refresh_url = Column(String, default='')
    remark = Column(String, default='备注')

    def serialize(self):
        return {
            'id': self.id,
            'source_folder': self.source_folder,
            'linktype': self.linktype,
            'soft_prefix': self.soft_prefix,
            'output_folder': self.output_folder,
            'escape_folder': self.escape_folder,
            'escape_size': self.escape_size,
            'clean_others': self.clean_others,
            'replace_CJK': self.replace_CJK,
            'fix_series': self.fix_series,
            'refresh_url': self.refresh_url,
            'remark': self.remark
        }


class _AutoConfigs(db.Model):
    __tablename__ = 'autoconfigs'

    id = Column(Integer, primary_key=True)
    original = Column(String, default="", comment="需要替换的前缀")
    prefixed = Column(String, default="", comment="前缀")
    scrapingfolders = Column(String, default="", comment="以;间隔")
    transferfolders = Column(String, default="", comment="以;间隔")
    scrapingconfs = Column(String, default="", comment="以;间隔")
    transferconfs = Column(String, default="", comment="以;间隔")
    remark = Column(String, default='备注')

    def serialize(self):
        return {
            'id': self.id,
            'original': self.original,
            'prefixed': self.prefixed,
            'scrapingfolders': self.scrapingfolders,
            'transferfolders': self.transferfolders,
            'scrapingconfs': self.scrapingconfs,
            'transferconfs': self.transferconfs,
            'remark': self.remark
        }


class _LocalConfigs(db.Model):
    __tablename__ = 'localconfigs'

    id = Column(Integer, primary_key=True)
    tg_token = Column(String, default="")
    tg_chatid = Column(String, default="")
    wechat_corpid = Column(String, default="")
    wechat_corpsecret = Column(String, default="")
    wechat_agentid = Column(String, default="")

    proxy_enable = Column(Boolean, default=False)
    proxy_type = Column(String, default='socks5h')
    proxy_address = Column(String, default='127.0.0.1:1080')

    task_clean = Column(Boolean, default=False)

    tr_url = Column(String, default="")
    tr_username = Column(String, default="")
    tr_passwd = Column(String, default="")
    tr_prefix = Column(String, default="")

    def serialize(self):
        return {
            'id': self.id,
            'tg_token': self.tg_token,
            'tg_chatid': self.tg_chatid,
            'wechat_corpid': self.wechat_corpid,
            'wechat_corpsecret': self.wechat_corpsecret,
            'wechat_agentid': self.wechat_agentid,
            'proxy_enable': self.proxy_enable,
            'proxy_type': self.proxy_type,
            'proxy_address': self.proxy_address,
            'task_clean': self.task_clean,
            'tr_url': self.tr_url,
            'tr_username': self.tr_username,
            'tr_passwd': self.tr_passwd,
            'tr_prefix': self.tr_prefix,
        }
