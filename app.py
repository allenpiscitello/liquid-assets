from flask import Flask, render_template
import json
import sqlite3

app = Flask(__name__)

with open("config.json") as configfile:
    config = json.load(configfile)

@app.route("/")
def view_assets():
    db = sqlite3.connect(config["database"])
    assets = db.execute("SELECT asset FROM issuances WHERE token IS NOT NULL ORDER BY datetime ASC")
    return render_template("all_assets.jinja", assets=assets)

@app.route("/asset/<string:id>")
def view_asset(id):
    db = sqlite3.connect(config["database"])
    #get reissuance token id
    token_info = db.execute("SELECT token, tokenamount FROM issuances WHERE asset=? AND token IS NOT NULL", (id, )).fetchone()
    assets = db.execute("SELECT block, datetime, amount FROM issuances WHERE asset=? ORDER BY datetime ASC", (id, ))
    reissuances = db.execute("SELECT block, datetime, amount FROM issuances WHERE asset=?", (token_info[0], ))
    return render_template("asset_details.jinja", asset_transactions = assets, reissuances=reissuances, token_info=token_info, asset_id=id)