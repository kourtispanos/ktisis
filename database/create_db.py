import sqlite3

from db import get_connection, DB_PATH


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_id INTEGER,
            location TEXT,
            start_date TEXT,
            status TEXT,
            budget REAL,
            end_date TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN end_date TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            daily_wage REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wage_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            work_date TEXT NOT NULL,
            days REAL NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (worker_id) REFERENCES workers (id),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            category TEXT,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            description TEXT,
            quantity REAL,
            unit TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    for column in ("quantity REAL", "unit TEXT"):
        try:
            cursor.execute(f"ALTER TABLE expenses ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            client_id INTEGER,
            amount REAL NOT NULL,
            income_date TEXT NOT NULL,
            description TEXT,
            vat_rate REAL,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE income ADD COLUMN vat_rate REAL")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            title TEXT NOT NULL,
            event_type TEXT,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            license_plate TEXT,
            insurance_expiry TEXT,
            kteo_expiry TEXT,
            road_tax_expiry TEXT,
            last_service_date TEXT,
            service_notes TEXT,
            notes TEXT
        )
    """)
    for column in ("last_service_date TEXT", "service_notes TEXT", "road_tax_expiry TEXT"):
        try:
            cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            project_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            vat_rate REAL,
            invoice_date TEXT NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tax_type TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"Η βάση δημιουργήθηκε: {DB_PATH}")


if __name__ == "__main__":
    create_tables()
