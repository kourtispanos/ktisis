import os
import sqlite3
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

from auth import hash_password, verify_password


def add_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    conn.close()
    if row is None:
        return False
    return verify_password(password, row[0])
