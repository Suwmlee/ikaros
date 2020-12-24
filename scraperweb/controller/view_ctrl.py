
from flask import render_template
from . import web


@web.route("/")
def index():
    return render_template('index.html')
