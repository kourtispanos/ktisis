import os
import sqlite3
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def add_client(name, phone=None, email=None, address=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO clients (name, phone, email, address) VALUES (?, ?, ?, ?)",
        (name, phone, email, address)
    )

    conn.commit()
    conn.close()


def update_client(client_id, name, phone=None, email=None, address=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE clients SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?",
        (name, phone, email, address, client_id)
    )

    conn.commit()
    conn.close()


def delete_client(client_id):
    # False αν έχει συνδεδεμένα έργα (FOREIGN KEY)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def list_clients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clients")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_client_balances():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.name,
            COALESCE((SELECT SUM(p.budget) FROM projects p WHERE p.client_id = c.id), 0) AS total_budget,
            COALESCE((SELECT SUM(i.amount) FROM income i WHERE i.client_id = c.id), 0) AS total_paid
        FROM clients c
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for client_id, name, total_budget, total_paid in rows:
        balance = total_budget - total_paid
        result.append((client_id, name, total_budget, total_paid, balance))
    return result
