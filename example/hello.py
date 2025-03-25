# coding:utf-8

import os

from flask import Flask
from flask import render_template_string
from xhtml import Template

BASE: str = os.path.dirname(__file__)
TEMPLATE: Template = Template()


app = Flask(__name__)


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return app.response_class(TEMPLATE.favicon.loadb(), mimetype='image/vnd.microsoft.icon')  # noqa:E501


@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def hello(path: str):
    return render_template_string(TEMPLATE.seek("hello.html").loads())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
