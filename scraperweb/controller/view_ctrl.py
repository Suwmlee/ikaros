
from . import web
from flask import render_template
from ..bizlogic.setting import settingService


@web.route("/")
def index():
    return render_template('index.html')

@web.route("/setting")
def setting():

    settings = settingService.getSetting()

    return render_template('setting.html', settings = settings)

@web.route("/scraper")
def scraper():
    return render_template('scraper.html')

@web.route("/history")
def history():
    return render_template('history.html')

@web.route("/transfer")
def transfer():
    return render_template('transfer.html')
