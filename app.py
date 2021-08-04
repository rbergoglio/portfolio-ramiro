from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#$env:FLASK_ENV = "development"
#flask run

counter = 0

@app.route("/")
def home():
    return render_template("home.html", message="hola")


@app.route("/date")
def date():
    return "<p>Hello, World!</p>" + str(datetime.now())


@app.route("/count-views")
def count_demo():
    global counter
    counter += 1
    return "<p>This page was visited</p>" + str(counter)