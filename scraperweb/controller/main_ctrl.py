
import json
from . import web
from flask import render_template, request
from ..bizlogic  import manager
from ..bizlogic.setting import settingService

@web.route("/start", methods=['POST'])
def start():
    content = request.get_json()

    settingService.updateScrapeFolder(content)

    manager.start()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 