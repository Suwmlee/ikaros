# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean
from .. import db


class _Settings(db.Model):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    main_mode = Column(Integer, default=1)
    debug_info = Column(Boolean, default=False)
    auto_exit = Column(Boolean, default=True)

    scrape_folder = Column(String, default='/jav')
    failed_folder = Column(String, default='failed')
    success_folder = Column(String, default='output')
    soft_link = Column(Boolean, default=False)
    failed_move = Column(Boolean, default=False)

    proxy_enable = Column(Boolean, default=False)
    proxy_type = Column(String, default='http')
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
