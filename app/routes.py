from flask import Blueprint, url_for, render_template, render_template_string, session, request, redirect, make_response, current_app
from app.db import get_db
import json
from functools import wraps
from app.preprocess_data import generate_data
from app.email_data import email_data

home = Blueprint('home', __name__, template_folder='templates')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('home.index'))

        return f(*args, **kwargs)

    return decorated


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
@requires_auth
def dashboard():
    return render_template("dashboard.html")


@home.route("/generate", methods=["GET", "POST"])
@requires_auth
def generate():

    url = request.form.get("url")
    week = int(request.form.get("week"))
    
    generate_data(url, week)
    
    return "Files generated!"


@home.route("/email", methods=["GET", "POST"])
@requires_auth
def email():

    week = int(request.form.get("week"))
    
    email_data(week)
    
    return "Files emailed!"
