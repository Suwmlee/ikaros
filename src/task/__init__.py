# -*- coding: utf-8 -*-
"""The job module."""

from .daily import DailyTask


def init_task(app):
    """ init task
    """
    scheduler = DailyTask(app)
    scheduler.start()
