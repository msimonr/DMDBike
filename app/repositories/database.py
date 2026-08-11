import sqlite3

from flask import current_app


def get_connection():
    return sqlite3.connect(current_app.config["DB_PATH"])
