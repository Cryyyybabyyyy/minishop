"""WSGI entry point for MiniShop."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Development only – Docker uses gunicorn
    app.run(host="127.0.0.1", port=5000, debug=False)
