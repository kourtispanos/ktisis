import os
import sqlite3
import sys

if getattr(sys, "frozen", False):
    # Μέσα σε πακεταρισμένο exe: το __file__ δείχνει σε προσωρινό φάκελο
    # εξαγωγής. Χρησιμοποιούμε το φάκελο του ίδιου του .exe.
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(APP_DIR, "ktisis.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
