import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def add_tax(tax_type, amount, due_date, paid=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO taxes (tax_type, amount, due_date, paid) VALUES (?, ?, ?, ?)",
        (tax_type, amount, due_date, paid)
    )

    conn.commit()
    conn.close()


def update_tax(tax_id, tax_type, amount, due_date, paid=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE taxes SET tax_type = ?, amount = ?, due_date = ?, paid = ? WHERE id = ?",
        (tax_type, amount, due_date, paid, tax_id)
    )

    conn.commit()
    conn.close()


def delete_tax(tax_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM taxes WHERE id = ?", (tax_id,))

    conn.commit()
    conn.close()


def list_taxes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM taxes")
    rows = cursor.fetchall()

    conn.close()
    return rows
