
from . import web
from flask import render_template
from ..bizlogic.setting import settingService


@web.route("/")
def index():

    folderpath = settingService.getSetting().scrape_folder

    return render_template('index.html', folderpath = folderpath)
