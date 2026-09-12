import datetime
import os
import sqlite3
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def add_project(name, client_id=None, location=None, start_date=None, status=None, budget=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO projects (name, client_id, location, start_date, status, budget, end_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, client_id, location, start_date, status, budget, end_date)
    )

    conn.commit()
    conn.close()


def update_project(
    project_id, name, client_id=None, location=None, start_date=None,
    status=None, budget=None, end_date=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE projects
           SET name = ?, client_id = ?, location = ?, start_date = ?, status = ?, budget = ?, end_date = ?
           WHERE id = ?""",
        (name, client_id, location, start_date, status, budget, end_date, project_id)
    )

    conn.commit()
    conn.close()


def delete_project(project_id):
    # False αν έχει συνδεδεμένα ημερομίσθια/έξοδα/έσοδα
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def list_projects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_project_financials():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id, p.name, p.budget,
            COALESCE((SELECT SUM(e.amount) FROM expenses e WHERE e.project_id = p.id), 0) AS total_expenses,
            COALESCE((SELECT SUM(w.amount) FROM wage_entries w WHERE w.project_id = p.id), 0) AS total_wages,
            COALESCE((SELECT SUM(i.amount) FROM income i WHERE i.project_id = p.id), 0) AS total_income
        FROM projects p
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for project_id, name, budget, expenses, wages, income in rows:
        spent = expenses + wages
        spent_pct = (spent / budget * 100) if budget else None
        remaining = (budget - spent) if budget else None
        result.append({
            "project_id": project_id,
            "name": name,
            "budget": budget,
            "expenses": expenses,
            "wages": wages,
            "income": income,
            "spent": spent,
            "spent_pct": spent_pct,
            "remaining": remaining,
        })
    return result


def calculate_working_days(start_date_str, end_date_str):
    if not start_date_str or not end_date_str:
        return None

    start = datetime.date.fromisoformat(start_date_str)
    end = datetime.date.fromisoformat(end_date_str)
    if end < start:
        return None

    working_days = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Δευτέρα ... 4=Παρασκευή
            working_days += 1
        current += datetime.timedelta(days=1)
    return working_days
