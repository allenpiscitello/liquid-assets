from flask import Flask, render_template
import json
import sqlite3

app = Flask(__name__)

with open("config.json") as configfile:
    config = json.load(configfile)

@app.route("/")
def view_assets():
    db = sqlite3.connect(config["database"])
    assets = db.execute("SELECT asset FROM issuances WHERE token IS NOT NULL ORDER BY datetime DESC")
    return render_template("all_assets.jinja", assets=assets)

@app.route("/asset/<string:id>")
def view_asset(id):
    return "hello"  + id