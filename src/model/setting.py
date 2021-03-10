# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean
from .. import db


class _Settings(db.Model):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    main_mode = Column(Integer, default=1)
    debug_info = Column(Boolean, default=False)
    auto_exit = Column(Boolean, default=True)

    scrape_folder = Column(String, default='/media')
    failed_folder = Column(String, default='/media/failed')
    success_folder = Column(String, default='/media/output')
    soft_link = Column(Boolean, default=True)
    soft_prefix = Column(String, default='/media')
    failed_move = Column(Boolean, default=False)

    proxy_enable = Column(Boolean, default=False)
    proxy_type = Column(String, default='socks5')
    proxy_address = Column(String, default='127.0.0.1:1080')
    proxy_timeout = Column(Integer, default=5)
    proxy_retry = Column(Integer, default=3)

    location_rule = Column(String, default="actor+'/'+number+' '+title")
    naming_rule = Column(String, default="number+' '+title")
    max_title_len = Column(Integer, default=50)
    update_check = Column(Boolean, default=False)
    website_priority = Column(String, default="javbus,javdb,fanza,xcity,mgstage,fc2,jav321,javlib,dlsite")

    escape_folders = Column(String, default="failed,output")
    escape_literals = Column(String, default="\()/")

    transalte_enable = Column(Boolean, default=False)
    transalte_to_sc = Column(Boolean, default=False)
    transalte_values = Column(String, default="title,outline")


    def serialize(self):
        return {
            'soft_link': self.soft_link,
            'soft_prefix': self.soft_prefix,
            'scrape_folder': self.scrape_folder,
            'success_folder': self.success_folder,
            'failed_folder': self.failed_folder,
            'location_rule': self.location_rule,
            'naming_rule': self.naming_rule,
            'proxy_enable':self.proxy_enable,
            'proxy_type':self.proxy_type,
            'proxy_address':self.proxy_address,
            'proxy_timeout':self.proxy_timeout,
            'proxy_retry':self.proxy_retry
        }


class _TransferSettings(db.Model):
    __tablename__ = 'transfersettings'

    id = Column(Integer, primary_key=True)
    source_folder = Column(String, default='/media')
    soft_prefix = Column(String, default='volume1/media')
    output_folder = Column(String, default='/media/output')
    escape_folder = Column(String, default='')
    mark = Column(String, default='默认配置')
