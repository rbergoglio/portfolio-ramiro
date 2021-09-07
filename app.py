#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#.venv\scripts\activate        
#$env:FLASK_ENV = "development"
#flask run


#pip freeze > requirements.txt
#pip install -r requirements.txt

import pdb
from datetime import datetime
from flask import Flask, render_template, abort, jsonify, request, redirect, url_for

app = Flask(__name__)

from model import db, save_db

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

@app.route("/item/new",methods=["GET","POST"])
def new_item():
    if request.method == "POST":
       # pdb.set_trace()
       #
        return redirect(url_for('home'))
    else:
        return render_template("new_item.html")

@app.route("/remove_card/<int:index>",methods=["GET","POST"])
def remove_card(index):
    try:
        if request.method == "POST":
            del db[index]
            save_db()
            return redirect(url_for('home'))
        else:
            return render_template("remove_card.html", card=db[index])
    except IndexError:
        abort(404)