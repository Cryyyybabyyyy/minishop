"""
Application configuration.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "minishop-lab-secret-key-change-in-prod")
    DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "instance", "minishop.db"))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "app", "static", "uploads"))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    # Intentionally permissive for the unrestricted-upload vulnerability demo
    ALLOWED_EXTENSIONS = None  # no extension check in vulnerable version
