import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

DEFAULT_VAT_RATE = 24.0


def add_income(project_id, amount, income_date, client_id=None, description=None, vat_rate=DEFAULT_VAT_RATE):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO income (project_id, client_id, amount, income_date, description, vat_rate)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (project_id, client_id, amount, income_date, description, vat_rate)
    )

    conn.commit()
    conn.close()


def update_income(
    income_id, project_id, amount, income_date, client_id=None,
    description=None, vat_rate=DEFAULT_VAT_RATE
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE income
           SET project_id = ?, client_id = ?, amount = ?, income_date = ?, description = ?, vat_rate = ?
           WHERE id = ?""",
        (project_id, client_id, amount, income_date, description, vat_rate, income_id)
    )

    conn.commit()
    conn.close()


def delete_income(income_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))

    conn.commit()
    conn.close()


def list_income():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM income")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_total_vat_reserve():
    total = 0.0
    for row in list_income():
        amount = row[3]
        vat_rate = row[6]
        if vat_rate:
            total += amount * vat_rate / 100
    return total
