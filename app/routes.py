from flask import Blueprint, url_for, render_template, render_template_string, session, request, redirect, make_response, current_app
from app.db import get_db
import json


home = Blueprint('home', __name__, template_folder='templates')

@home.route("/")
def index():

    if session.get("user") is not None:
        return redirect(url_for("home.dashboard"))

    return render_template("index.html")



@home.route("/login", methods=["GET", "POST"])
def login():


    username = request.form.get("username")
    password = request.form.get("password")


    db = get_db()
    cur = db.cursor()
    
    user = cur.execute("SELECT * FROM user WHERE username = ?", (username, )).fetchone()
    users = cur.execute("SELECT * FROM user").fetchall()
    print("\n\n\n")
    for u in users:
        print(u["username"], ["password"])

    if user is None:
        return "Invalid username"
    if user["password"] != password:
        return "Invalid password"


    del user["password"]

    session["user"] = user
    session.modified = True

    r = make_response()
    r.headers.set("HX-Redirect", url_for("home.dashboard"))
    return r






@home.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("home.html")
