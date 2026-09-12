import os
import sqlite3
import sys

if getattr(sys, "frozen", False):
    # Το Program Files (εκεί όπου συνήθως εγκαθίσταται το exe) δεν
    # επιτρέπει εγγραφή σε απλούς χρήστες - η βάση πρέπει να ζει σε
    # προσωπικό, εγγράψιμο φάκελο.
    DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Ktisis")
    os.makedirs(DATA_DIR, exist_ok=True)
else:
    DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(DATA_DIR, "ktisis.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
