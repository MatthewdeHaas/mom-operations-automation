from flask import Blueprint, url_for, render_template, render_template_string, session, request, redirect, make_response, current_app, send_file
from app.db import get_db
import json
from functools import wraps
import os
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

    # TODO: Uncomment and replace in production
    if "email" in request.form:
        # email_data(f"data/week_{week}", "sam@mealsonthemove.ca")
        email_data(f"data/week_{week}.zip")
        return "Files Generated and shared with your email!"

    return "Files Generated!"


@home.route("/download/<week>", methods=["GET", "POST"])
@requires_auth
def download(week):

    basedir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(basedir, "..", "data", f"week_{week}.zip")
    file_path = os.path.normpath(file_path) 

    return send_file(file_path, as_attachment=True, download_name=f"week_{week}.zip")

