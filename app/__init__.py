import os
import secrets
from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__, static_folder="", instance_path="/app")

    app.config["SECRET_KEY"] = "prod"
    app.config["DATABASE"] = "app/instance/prod.db"

    # register database
    from app.db import init_app
    init_app(app) 

    # register blueprints
    from app.routes import home
    app.register_blueprint(home)

    return app
