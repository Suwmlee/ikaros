
import os
from flask import render_template, Response
from . import web


@web.route("/")
def index():
    return render_template('index.html')


@web.route("/imgs/<imageid>")
def imgs(imageid):
    localPath = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(localPath, "..", "..", "docs", "imgs", imageid), 'rb') as f:
        image = f.read()
    resp = Response(image, mimetype="image/jpeg")
    return resp
