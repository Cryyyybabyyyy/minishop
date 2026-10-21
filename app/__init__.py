"""
MiniShop - Intentionally Vulnerable E-Commerce Application
==========================================================
FOR AUTHORISED SECURITY TESTING / UNIVERSITY SSDLC LAB ONLY.
DO NOT EXPOSE TO THE PUBLIC INTERNET.
"""

from flask import Flask
from app.config import Config
from app.models import init_db, close_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload folders exist
    import os
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    # Initialise database (creates tables + seeds if empty)
    with app.app_context():
        init_db()

    app.teardown_appcontext(close_db)

    # Register blueprints / routes
    from app.routes import bp
    app.register_blueprint(bp)

    return app
