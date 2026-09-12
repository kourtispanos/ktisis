import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

EXPENSE_CATEGORIES = [
    "Υλικά (γενικά)",
    "Προμήθεια σιδήρου",
    "Τσιμέντο / Σκυρόδεμα",
    "Ξυλεία",
    "Ηλεκτρολόγος",
    "Υδραυλικός",
    "Χωματουργικά",
    "Μίσθωση μηχανημάτων",
    "Μεταφορικά",
    "Λοιπά",
]


def add_expense(project_id, amount, expense_date, category=None, description=None, quantity=None, unit=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO expenses (project_id, category, amount, expense_date, description, quantity, unit)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (project_id, category, amount, expense_date, description, quantity, unit)
    )

    conn.commit()
    conn.close()


def update_expense(
    expense_id, project_id, amount, expense_date, category=None,
    description=None, quantity=None, unit=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE expenses
           SET project_id = ?, category = ?, amount = ?, expense_date = ?, description = ?,
               quantity = ?, unit = ?
           WHERE id = ?""",
        (project_id, category, amount, expense_date, description, quantity, unit, expense_id)
    )

    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    conn.commit()
    conn.close()


def list_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    conn.close()
    return rows
