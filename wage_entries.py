import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def add_wage_entry(worker_id, project_id, work_date, days, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO wage_entries (worker_id, project_id, work_date, days, amount)
           VALUES (?, ?, ?, ?, ?)""",
        (worker_id, project_id, work_date, days, amount)
    )

    conn.commit()
    conn.close()


def update_wage_entry(entry_id, worker_id, project_id, work_date, days, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE wage_entries
           SET worker_id = ?, project_id = ?, work_date = ?, days = ?, amount = ?
           WHERE id = ?""",
        (worker_id, project_id, work_date, days, amount, entry_id)
    )

    conn.commit()
    conn.close()


def delete_wage_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM wage_entries WHERE id = ?", (entry_id,))

    conn.commit()
    conn.close()


def list_wage_entries():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM wage_entries")
    rows = cursor.fetchall()

    conn.close()
    return rows
