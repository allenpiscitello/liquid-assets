from flask import Flask

app = Flask(__name__)


@app.route("/")
def view_assets():
    return "all assets"

@app.route("/asset/<string:id>")
def view_asset(id):
    return "hello"  + id