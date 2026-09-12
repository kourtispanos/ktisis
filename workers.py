import os
import sqlite3
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def add_worker(name, specialty=None, daily_wage=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO workers (name, specialty, daily_wage) VALUES (?, ?, ?)",
        (name, specialty, daily_wage)
    )

    conn.commit()
    conn.close()


def update_worker(worker_id, name, specialty=None, daily_wage=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE workers SET name = ?, specialty = ?, daily_wage = ? WHERE id = ?",
        (name, specialty, daily_wage, worker_id)
    )

    conn.commit()
    conn.close()


def delete_worker(worker_id):
    # False αν έχει συνδεδεμένα ημερομίσθια
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def list_workers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workers")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_worker_totals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            w.id, w.name, w.specialty, w.daily_wage,
            COALESCE((SELECT SUM(e.days) FROM wage_entries e WHERE e.worker_id = w.id), 0) AS total_days,
            COALESCE((SELECT SUM(e.amount) FROM wage_entries e WHERE e.worker_id = w.id), 0) AS total_amount
        FROM workers w
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
