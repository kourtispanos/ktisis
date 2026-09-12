import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

DEFAULT_VAT_RATE = 24.0


def add_invoice(invoice_number, project_id, amount, invoice_date, vat_rate=DEFAULT_VAT_RATE, paid=0, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO invoices (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes)
    )

    conn.commit()
    conn.close()


def update_invoice(
    invoice_id, invoice_number, project_id, amount, invoice_date,
    vat_rate=DEFAULT_VAT_RATE, paid=0, notes=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE invoices
           SET invoice_number = ?, project_id = ?, amount = ?, vat_rate = ?,
               invoice_date = ?, paid = ?, notes = ?
           WHERE id = ?""",
        (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes, invoice_id)
    )

    conn.commit()
    conn.close()


def delete_invoice(invoice_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))

    conn.commit()
    conn.close()


def list_invoices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invoices ORDER BY invoice_date DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_total_unpaid():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE paid = 0")
    total = cursor.fetchone()[0]

    conn.close()
    return total
