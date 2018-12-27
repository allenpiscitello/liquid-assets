from flask import Flask

app = Flask(__name__)

@app.route("/asset/<string:id>")
def view_asset(id):
    return "hello"  + id