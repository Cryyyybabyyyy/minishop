"""
Database models and initialisation for MiniShop.
Uses SQLite with a simple schema and synthetic seed data.
"""

import sqlite3
import os
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    """Return a connection to the SQLite database, cached on flask.g."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed synthetic data if the database is empty."""
    db_path = current_app.config["DATABASE"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # Users table (includes optional profile picture)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'seller')),
            profile_image TEXT
        )
        """
    )

    # Products table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_filename TEXT,
            stock INTEGER DEFAULT 10
        )
        """
    )

    # Orders table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            total REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    # Order items table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """
    )

    db.commit()

    # Seed only if no users exist
    cur.execute("SELECT COUNT(*) AS cnt FROM users")
    if cur.fetchone()["cnt"] == 0:
        _seed_data(db)

    db.close()


def _seed_data(db):
    """Insert synthetic accounts, products and orders."""
    cur = db.cursor()

    users = [
        ("alice", generate_password_hash("alice123"), "customer", None),
        ("bob", generate_password_hash("bob123"), "customer", None),
        ("seller", generate_password_hash("seller123"), "seller", None),
    ]
    cur.executemany(
        "INSERT INTO users (username, password_hash, role, profile_image) VALUES (?, ?, ?, ?)",
        users,
    )

    products = [
        (
            "Wireless Noise-Cancelling Headphones",
            "Premium over-ear headphones with active noise cancellation and 30-hour battery life.",
            129.99,
            "headphones.svg",
            25,
        ),
        (
            "Mechanical Gaming Keyboard",
            "RGB backlit mechanical keyboard with Cherry MX switches and programmable macros.",
            89.50,
            "keyboard.svg",
            40,
        ),
        (
            "Ultra-Slim Laptop Stand",
            "Aluminium ergonomic laptop stand with adjustable height and cable management.",
            34.99,
            "stand.svg",
            60,
        ),
        (
            "Portable SSD 1TB",
            "USB-C portable solid-state drive with 1050 MB/s read speeds and shock resistance.",
            109.00,
            "ssd.svg",
            30,
        ),
        (
            "Smart LED Desk Lamp",
            "App-controlled LED desk lamp with adjustable colour temperature and brightness.",
            45.75,
            "lamp.svg",
            50,
        ),
        (
            "Ergonomic Office Chair",
            "High-back mesh office chair with lumbar support and 4D armrests.",
            249.00,
            "chair.svg",
            15,
        ),
    ]
    cur.executemany(
        "INSERT INTO products (name, description, price, image_filename, stock) VALUES (?, ?, ?, ?, ?)",
        products,
    )

    cur.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (1, 'Delivered', 210.73)"
    )
    order1_id = cur.lastrowid
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [
            (order1_id, 1, 1, 129.99),
            (order1_id, 3, 1, 34.99),
            (order1_id, 5, 1, 45.75),
        ],
    )

    cur.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (1, 'Shipped', 89.50)"
    )
    order2_id = cur.lastrowid
    cur.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        (order2_id, 2, 1, 89.50),
    )

    cur.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (2, 'Processing', 358.00)"
    )
    order3_id = cur.lastrowid
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [
            (order3_id, 4, 1, 109.00),
            (order3_id, 6, 1, 249.00),
        ],
    )

    cur.execute(
        "INSERT INTO orders (user_id, status, total) VALUES (2, 'Delivered', 129.99)"
    )
    order4_id = cur.lastrowid
    cur.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        (order4_id, 1, 1, 129.99),
    )

    db.commit()
