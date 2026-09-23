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
    DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Το KTISIS_DB_PATH επιτρέπει σε δοκιμές να δουλεύουν σε άλλη βάση, χωρίς να αγγίξουν την πραγματική
DB_PATH = os.environ.get("KTISIS_DB_PATH") or os.path.join(DATA_DIR, "ktisis.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute(sql, params=()):
    """Τρέχει INSERT / UPDATE / DELETE και αποθηκεύει την αλλαγή."""
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def fetch_all(sql, params=()):
    """Τρέχει SELECT και επιστρέφει λίστα από γραμμές (tuples)."""
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def fetch_value(sql, params=()):
    """Τρέχει SELECT που επιστρέφει μία τιμή (π.χ. ένα SUM)."""
    return fetch_all(sql, params)[0][0]


def delete_row(table, row_id):
    """Διαγράφει μια εγγραφή. Επιστρέφει False αν χρησιμοποιείται αλλού (FOREIGN KEY)."""
    try:
        execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        return True
    except sqlite3.IntegrityError:
        return False
