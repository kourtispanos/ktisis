from backend.database.db import delete_row, execute, fetch_all


# ---------- Πελάτες ----------

def add_client(name, phone=None, email=None, address=None):
    execute(
        "INSERT INTO clients (name, phone, email, address) VALUES (?, ?, ?, ?)",
        (name, phone, email, address),
    )


def update_client(client_id, name, phone=None, email=None, address=None):
    execute(
        "UPDATE clients SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?",
        (name, phone, email, address, client_id),
    )


def delete_client(client_id):
    return delete_row("clients", client_id)  # False αν έχει συνδεδεμένα έργα


def list_clients():
    return fetch_all("SELECT * FROM clients")


def get_client_balances():
    rows = fetch_all("""
        SELECT
            c.id,
            c.name,
            COALESCE((SELECT SUM(p.budget) FROM projects p WHERE p.client_id = c.id), 0) AS total_budget,
            COALESCE((SELECT SUM(i.amount) FROM income i WHERE i.client_id = c.id), 0) AS total_paid
        FROM clients c
    """)
    return [
        (client_id, name, total_budget, total_paid, total_budget - total_paid)
        for client_id, name, total_budget, total_paid in rows
    ]


# ---------- Εργάτες ----------

def add_worker(name, specialty=None, daily_wage=None):
    execute(
        "INSERT INTO workers (name, specialty, daily_wage) VALUES (?, ?, ?)",
        (name, specialty, daily_wage),
    )


def update_worker(worker_id, name, specialty=None, daily_wage=None):
    execute(
        "UPDATE workers SET name = ?, specialty = ?, daily_wage = ? WHERE id = ?",
        (name, specialty, daily_wage, worker_id),
    )


def delete_worker(worker_id):
    return delete_row("workers", worker_id)  # False αν έχει συνδεδεμένα ημερομίσθια


def list_workers():
    return fetch_all("SELECT * FROM workers")


def get_worker_totals():
    return fetch_all("""
        SELECT
            w.id, w.name, w.specialty, w.daily_wage,
            COALESCE((SELECT SUM(e.days) FROM wage_entries e WHERE e.worker_id = w.id), 0) AS total_days,
            COALESCE((SELECT SUM(e.amount) FROM wage_entries e WHERE e.worker_id = w.id), 0) AS total_amount
        FROM workers w
    """)


# ---------- Ημερομίσθια ----------

def add_wage_entry(worker_id, project_id, work_date, days, amount):
    execute(
        "INSERT INTO wage_entries (worker_id, project_id, work_date, days, amount) VALUES (?, ?, ?, ?, ?)",
        (worker_id, project_id, work_date, days, amount),
    )


def update_wage_entry(entry_id, worker_id, project_id, work_date, days, amount):
    execute(
        """UPDATE wage_entries
           SET worker_id = ?, project_id = ?, work_date = ?, days = ?, amount = ?
           WHERE id = ?""",
        (worker_id, project_id, work_date, days, amount, entry_id),
    )


def delete_wage_entry(entry_id):
    return delete_row("wage_entries", entry_id)


def list_wage_entries():
    return fetch_all("SELECT * FROM wage_entries")
