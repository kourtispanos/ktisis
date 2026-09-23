import sqlite3

from backend.auth.auth import hash_password, verify_password
from backend.database.db import execute, fetch_all


def add_user(username, password):
    """Δημιουργεί χρήστη. Επιστρέφει False αν το όνομα χρήστη υπάρχει ήδη."""
    try:
        execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def check_login(username, password):
    rows = fetch_all("SELECT password_hash FROM users WHERE username = ?", (username,))
    return bool(rows) and verify_password(password, rows[0][0])


def delete_user(username, password):
    """Διαγράφει τον λογαριασμό αν ο κωδικός είναι σωστός. Δεν αγγίζει τα δεδομένα της εργολαβίας."""
    if not check_login(username, password):
        return False
    execute("DELETE FROM users WHERE username = ?", (username,))
    return True
