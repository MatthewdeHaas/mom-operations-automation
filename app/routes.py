
from flask import Blueprint, url_for, render_template
from app.db import get_db
import json

home = Blueprint('home', __name__, template_folder='templates')

@home.route("/")
def index():

    db = get_db()
    cur = db.cursor()

    print(cur.execute("SELECT * FROM week_4").fetchone()["Customer"])

    return render_template("index.html")
