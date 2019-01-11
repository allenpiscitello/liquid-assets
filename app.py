from flask import Flask, render_template
import json
import sqlite3
import datetime

app = Flask(__name__)

with open("config.json") as configfile:
    config = json.load(configfile)

@app.template_filter('timestamp')
def timestamp_filter(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d %H:%M")

@app.template_filter('confidential_amount')
def confidential_filter(amount):
    return "Confidential" if amount == None else "{0:,}".format(amount)

@app.route("/")
def view_assets():
    db = sqlite3.connect(config["database"])
    assets = db.execute("SELECT block, datetime, t1.asset, CASE t3.confidential_count WHEN 1 THEN NULL ELSE t2.supply END AS supply, IFNULL(tokenamount, 0) + IFNULL(token_burns,0) > 0 as reuissuable, IFNULL(tokenamount, 0) > 0 AS originally_reissuable FROM (SELECT block, datetime, asset, token, tokenamount FROM issuances WHERE token IS NOT NULL) t1 LEFT JOIN (SELECT asset, SUM(amount) AS supply FROM issuances WHERE token IS NOT NULL GROUP BY asset) t2 ON t1.asset=t2.asset LEFT JOIN  (SELECT asset, COUNT(*) > 0 confidential_count FROM issuances WHERE amount IS NULL GROUP BY asset) t3 ON t3.asset=t1.asset LEFT JOIN (SELECT asset, SUM(amount) AS token_burns FROM issuances WHERE asset IN (SELECT token FROM issuances)) t4 ON t1.token=t4.asset ORDER BY datetime ASC")
    return render_template("all_assets.jinja", assets=assets)


class AssetInfoViewModel:
    def __init__(self, db, asset_id):
        
        self.id = asset_id
        confiential_issues = db.execute("SELECT COUNT(*) FROM issuances WHERE amount IS NULL AND asset=?", (asset_id,)).fetchone()[0]
        if confiential_issues > 0:
            self.supply = None
        else:
            self.supply = db.execute("SELECT SUM(amount) FROM issuances WHERE asset=?", (asset_id,)).fetchone()[0]

        token_info = db.execute("SELECT token, tokenamount, block, datetime FROM issuances WHERE asset=? AND token IS NOT NULL", (asset_id, )).fetchone()
        self.reissuable = token_info[1] != None
        self.reissuanceToken = token_info[0]
        self.reissueAmount = token_info[1]
        self.creationBlock = token_info[2]
        self.creationTime = token_info[3]
        reissuable_supply = db.execute("SELECT SUM(amount) FROM issuances WHERE asset=?", (token_info[0],)).fetchone()[0]
        self.reissuanceSupply = (0 if reissuable_supply == None else reissuable_supply) + (0 if token_info[1] == None else token_info[1])
        self.reissuances = db.execute("SELECT block, datetime, amount FROM issuances WHERE asset=?", (token_info[0], )).fetchall()
        self.assetTransactions =  db.execute("SELECT block, datetime, amount FROM issuances WHERE asset=? ORDER BY datetime ASC", (asset_id, )).fetchall()

@app.route("/asset/<string:id>")
def view_asset(id):
    db = sqlite3.connect(config["database"])
    #get reissuance token id
    asset_info = AssetInfoViewModel(db, id)

    return render_template("asset_details.jinja", asset = asset_info)