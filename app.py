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

from wtforms import StringField, TextAreaField, SubmitField, SelectField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

class NewItemForm(FlaskForm):
    title           = StringField("Title", validators=[InputRequired("Input is invalid"), DataRequired("Data is required"), Length(min=5, max=20, message="Input must be between 5 and 20 characters long")])
    price           = DecimalField("Price")
    description     = TextAreaField("Description", validators=[InputRequired("Input is invalid"), DataRequired("Data is required"), Length(min=5, max=40, message="Input must be between 5 and 40 characters long")])
    category        = SelectField("Category", coerce=int)
    subcategory     = SelectField("Subcategory", coerce=int)
    submit          = SubmitField("Submit")

class DeleteItemForm(FlaskForm):
    submit          = SubmitField("Delete item")

@app.route("/item/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    conn = get_db()
    c = conn.cursor()

    item_from_db = c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = c.fetchone()
    try:
        item = {
            "id": row[0],
            "title": row[1]
        }
    except:
        item = {}

    if item:
        c.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        
        flash("Item {} has been successfully deleted.".format(item["title"]), "success")

    else:
        flash("This item does not exist.","danger")

    return redirect(url_for("home"))        


@app.route("/item/<int:item_id>")
def item(item_id):
    c = get_db().cursor()
    item_from_db = c.execute(""" SELECT
                    i.id, i.title, i.description, i.price, i.image, c.name, c.id, s.name, s.id
                    FROM
                    items AS i
                    INNER JOIN categories     AS c ON i.category_id     = c.id
                    INNER JOIN subcategories  AS s ON i.subcategory_id  = s.id
                    WHERE i.id = ?""",(item_id,)
    )
    row = c.fetchone()

    try:
        item = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": row[3],
            "image": row[4],
            "category": row[5],
            "subcategory": row[7]
        }
    except:
        item = {}

    if item:
        deleteItemForm = DeleteItemForm()

        return render_template("item.html", item= item, deleteItemForm= deleteItemForm)
    return redirect(url_for("home"))


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
            "title": row[1],
            "description": row[2],
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

    c.execute(""" SELECT id, name FROM categories """)
    categories = c.fetchall()

    form.category.choices = categories

    c.execute(""" SELECT id, name FROM subcategories WHERE category_id = ?""",(2,))
    subcategories = c.fetchall()

    form.subcategory.choices = subcategories

    #if request.method == "POST":
    #validate_on_submit -> consider submitted if the request is POST, PUT, PATCH delete AND calls validate on each field if it was submitted
    if form.validate_on_submit():
        # pdb.set_trace()
        c.execute(""" INSERT INTO items (title, description, price, image, category_id, subcategory_id) VALUES (?,?,?,?,?,?) """,
        (
            form.title.data,
            form.description.data,
            float(form.price.data),
            "",
            form.category.data,
            form.subcategory.data
        )) 
        conn.commit()
        flash("Item {} has ben succesfully submitted".format(request.form.get("title")), "success"),
        return redirect(url_for('home'))
    
    #errores del validate
    if form.errors:
        flash("{}".format(form.errors),"danger")

    return render_template("new_item.html", form=form)


def get_db():
    #hay que fijarse si ya existe una conexion en el contexto de la app "g", si no existe se crea
    db = getattr(g,"_database", None)
    if db is None:
        db = g.database = sqlite3.connect("db/rbwebshop.db")
    return db

#este decorador hace que se ejecute cuando termina el contexto de la app.  cuando la request termina esta funcion va a cerrar la conexión 
@app.teardown_appcontext   
def close_connection(exception):
    db = getattr(g,"_database", None)
    if db is not None:
        db.close()

