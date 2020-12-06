
from . import web
from flask import render_template
from ..bizlogic.setting import settingService


@web.route("/")
def index():

    settings = settingService.getSetting()

    return render_template('index.html', settings = settings)
