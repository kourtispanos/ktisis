from backend.database.db import delete_row, execute, fetch_all, fetch_value

DEFAULT_VAT_RATE = 24.0


# ---------- Έξοδα ----------

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
    execute(
        """INSERT INTO expenses (project_id, category, amount, expense_date, description, quantity, unit)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (project_id, category, amount, expense_date, description, quantity, unit),
    )


def update_expense(
    expense_id, project_id, amount, expense_date, category=None,
    description=None, quantity=None, unit=None,
):
    execute(
        """UPDATE expenses
           SET project_id = ?, category = ?, amount = ?, expense_date = ?, description = ?,
               quantity = ?, unit = ?
           WHERE id = ?""",
        (project_id, category, amount, expense_date, description, quantity, unit, expense_id),
    )


def delete_expense(expense_id):
    return delete_row("expenses", expense_id)


def list_expenses():
    return fetch_all("SELECT * FROM expenses")


# ---------- Έσοδα ----------

def add_income(project_id, amount, income_date, client_id=None, description=None, vat_rate=DEFAULT_VAT_RATE):
    execute(
        """INSERT INTO income (project_id, client_id, amount, income_date, description, vat_rate)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (project_id, client_id, amount, income_date, description, vat_rate),
    )


def update_income(
    income_id, project_id, amount, income_date, client_id=None,
    description=None, vat_rate=DEFAULT_VAT_RATE,
):
    execute(
        """UPDATE income
           SET project_id = ?, client_id = ?, amount = ?, income_date = ?, description = ?, vat_rate = ?
           WHERE id = ?""",
        (project_id, client_id, amount, income_date, description, vat_rate, income_id),
    )


def delete_income(income_id):
    return delete_row("income", income_id)


def list_income():
    return fetch_all("SELECT * FROM income")


def get_total_vat_reserve():
    """Συνολικός ΦΠΑ που πρέπει να μείνει στην άκρη, από όλα τα έσοδα."""
    return fetch_value("SELECT COALESCE(SUM(amount * COALESCE(vat_rate, 0) / 100), 0) FROM income")


# ---------- Τιμολόγια ----------

def add_invoice(invoice_number, project_id, amount, invoice_date, vat_rate=DEFAULT_VAT_RATE, paid=0, notes=None):
    execute(
        """INSERT INTO invoices (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes),
    )


def update_invoice(
    invoice_id, invoice_number, project_id, amount, invoice_date,
    vat_rate=DEFAULT_VAT_RATE, paid=0, notes=None,
):
    execute(
        """UPDATE invoices
           SET invoice_number = ?, project_id = ?, amount = ?, vat_rate = ?,
               invoice_date = ?, paid = ?, notes = ?
           WHERE id = ?""",
        (invoice_number, project_id, amount, vat_rate, invoice_date, paid, notes, invoice_id),
    )


def delete_invoice(invoice_id):
    return delete_row("invoices", invoice_id)


def list_invoices():
    return fetch_all("SELECT * FROM invoices ORDER BY invoice_date DESC")


def get_total_unpaid():
    return fetch_value("SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE paid = 0")


# ---------- Φορολογίες ----------

def add_tax(tax_type, amount, due_date, paid=0):
    execute(
        "INSERT INTO taxes (tax_type, amount, due_date, paid) VALUES (?, ?, ?, ?)",
        (tax_type, amount, due_date, paid),
    )


def update_tax(tax_id, tax_type, amount, due_date, paid=0):
    execute(
        "UPDATE taxes SET tax_type = ?, amount = ?, due_date = ?, paid = ? WHERE id = ?",
        (tax_type, amount, due_date, paid, tax_id),
    )


def delete_tax(tax_id):
    return delete_row("taxes", tax_id)


def list_taxes():
    return fetch_all("SELECT * FROM taxes")
