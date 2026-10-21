"""
Basic functional tests for MiniShop.
These tests verify that the application starts, pages render, and
authentication works. They do NOT attempt to exploit vulnerabilities.
"""

import os
import pytest
from app import create_app
from app.models import init_db


@pytest.fixture
def app(tmp_path):
    """Create an application configured for testing with a temporary DB."""
    db_path = tmp_path / "test.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    class TestConfig:
        SECRET_KEY = "test-secret"
        DATABASE = str(db_path)
        UPLOAD_FOLDER = str(upload_dir)
        MAX_CONTENT_LENGTH = 5 * 1024 * 1024
        TESTING = True
        WTF_CSRF_ENABLED = False

    application = create_app(TestConfig)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_page(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"MiniShop" in rv.data
    assert b"Product Catalogue" in rv.data


def test_login_page(client):
    rv = client.get("/login")
    assert rv.status_code == 200
    assert b"Sign In" in rv.data


def test_login_success_alice(client):
    rv = client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Welcome back, alice" in rv.data or b"alice" in rv.data


def test_login_failure(client):
    rv = client.post(
        "/login",
        data={"username": "alice", "password": "wrong"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Invalid username or password" in rv.data


def test_orders_requires_login(client):
    rv = client.get("/orders", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Please log in" in rv.data or b"Sign In" in rv.data


def test_seller_dashboard_requires_seller(client):
    # Login as customer
    client.post("/login", data={"username": "alice", "password": "alice123"})
    rv = client.get("/seller", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Access denied" in rv.data or b"Seller account required" in rv.data


def test_product_detail(client):
    rv = client.get("/product/1")
    assert rv.status_code == 200
    assert b"Wireless" in rv.data or b"Headphones" in rv.data


def test_404(client):
    rv = client.get("/product/9999")
    assert rv.status_code == 404
