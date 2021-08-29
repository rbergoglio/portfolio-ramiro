from datetime import datetime
from flask import Flask, render_template, abort,jsonify

app = Flask(__name__)

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#.venv\scripts\activate        
#$env:FLASK_ENV = "development"
#flask run

from model import db

counter = 0

@app.route("/")
def home():
    return render_template("home.html", cards=db)


@app.route("/date")
def date():
    return "<p>Hello, World!</p>" + str(datetime.now())

@app.route("/card/<int:index>")
def card_view(index):
    try:
        card = db[index]
        return render_template("card.html", card=card, index=index, max_index=len(db)-1)
    except IndexError:
        abort(404)



@app.route("/api/card")
def api_card_list():
    return jsonify(db)

@app.route("/api/card/<int:index>")
def api_card_detail(index):
    try:
        return db[index]
    except IndexError:
        abort(404)
