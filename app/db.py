import sqlite3
from flask import g
from pathlib import Path

db_path = "instance/app.db"

def db_connection():
    db = getattr(g, "_database", None)
    
    if db is None:
        # Check whether instance folder exists or not.
        Path("instance").mkdir(exist_ok=True)

        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

def db_close(error = None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
