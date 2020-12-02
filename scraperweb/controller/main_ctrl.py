
import json
from . import web
from flask import render_template

@web.route("/start")
def start():


    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 