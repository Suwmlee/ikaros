
import json
from . import web
from flask import render_template
from ..bizlogic  import service

@web.route("/start")
def start():

    service.start()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 