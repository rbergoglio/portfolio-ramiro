#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#.venv\scripts\activate        
#$env:FLASK_ENV = "development"
#flask run


#pip freeze > requirements.txt
#pip install -r requirements.txt

import pdb
from datetime import datetime
from flask import Flask, render_template, abort, jsonify, request, redirect, url_for, g, flash

from flask_wtf import FlaskForm

import sqlite3

from wtforms import StringField, TextAreaField, SubmitField

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

class NewItemForm(FlaskForm):
    title           = StringField("Title")
    price           = StringField("Price")
    description     = TextAreaField("Description")
    submit          = SubmitField("Submit")

@app.route("/")
def home():
    conn = get_db()
    c = conn.cursor()

    items_from_db = c.execute("""SELECT i.id, i.title, i.description, i.price, i.image, c.name, s.name
    FROM items AS i
    INNER JOIN categories AS c ON i.category_id = c.id 
    INNER JOIN subcategories AS s ON i.subcategory_id = s.id  
    ORDER BY i.id DESC""")

    items = []
    for row in items_from_db:
        item = {
            "id": row[0],
            "description": row[1],
            "price": row[3],
            "image":row[4],
            "category":row[5],
            "subcategory":row[6]
        }
        items.append(item)

    return render_template("home.html", items = items)


@app.route("/item/new",methods=["GET","POST"])
def new_item():
    conn = get_db()
    c = conn.cursor()

    form = NewItemForm()

    if request.method == "POST":
        # pdb.set_trace()
        c.execute(""" INSERT INTO items (title, description, price, image, category_id, subcategory_id) VALUES (?,?,?,?,?,?) """,
        (
            form.title.data,
            form.description.data,
            float(form.price.data),
            "",
            1,
            1
        )) 
        conn.commit()
        flash("Item {} has ben succesfully submitted".format(request.form.get("title")), "success"),
        return redirect(url_for('home'))
    else:
        return render_template("new_item.html", form=form)


def get_db():
    #hay que fijarse si ya existe una conexion en el contexto de la app "g", si no existe se crea
    db = getattr(g,"_database", None)
    if db is None:
        db = g.database = sqlite3.connect("db/rbwebshop.db")
    return db

#este decorador hace que se ejecute cuando termina el contexto de la app.  cuando la request termina esta funcion va a cerrar la coneccion 
@app.teardown_appcontext   
def close_connection(exception):
    db = getattr(g,"_database", None)
    if db is not None:
        db.close()

