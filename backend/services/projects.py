import datetime

from backend.database.db import delete_row, execute, fetch_all


def add_project(name, client_id=None, location=None, start_date=None, status=None, budget=None, end_date=None):
    execute(
        """INSERT INTO projects (name, client_id, location, start_date, status, budget, end_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, client_id, location, start_date, status, budget, end_date),
    )


def update_project(
    project_id, name, client_id=None, location=None, start_date=None,
    status=None, budget=None, end_date=None,
):
    execute(
        """UPDATE projects
           SET name = ?, client_id = ?, location = ?, start_date = ?, status = ?, budget = ?, end_date = ?
           WHERE id = ?""",
        (name, client_id, location, start_date, status, budget, end_date, project_id),
    )


def delete_project(project_id):
    return delete_row("projects", project_id)  # False αν έχει συνδεδεμένα ημερομίσθια/έξοδα/έσοδα


def list_projects():
    return fetch_all("SELECT * FROM projects")


def get_project_financials():
    rows = fetch_all("""
        SELECT
            p.id, p.name, p.budget,
            COALESCE((SELECT SUM(e.amount) FROM expenses e WHERE e.project_id = p.id), 0) AS total_expenses,
            COALESCE((SELECT SUM(w.amount) FROM wage_entries w WHERE w.project_id = p.id), 0) AS total_wages,
            COALESCE((SELECT SUM(i.amount) FROM income i WHERE i.project_id = p.id), 0) AS total_income
        FROM projects p
    """)

    result = []
    for project_id, name, budget, expenses, wages, income in rows:
        spent = expenses + wages
        result.append({
            "project_id": project_id,
            "name": name,
            "budget": budget,
            "expenses": expenses,
            "wages": wages,
            "income": income,
            "spent": spent,
            "spent_pct": (spent / budget * 100) if budget else None,
            "remaining": (budget - spent) if budget else None,
        })
    return result


def calculate_working_days(start_date_str, end_date_str):
    """Πλήθος εργάσιμων ημερών (Δευτέρα-Παρασκευή) από την έναρξη ως την ολοκλήρωση, συμπεριλαμβανομένων."""
    if not start_date_str or not end_date_str:
        return None

    start = datetime.date.fromisoformat(start_date_str)
    end = datetime.date.fromisoformat(end_date_str)
    if end < start:
        return None

    all_days = (start + datetime.timedelta(days=i) for i in range((end - start).days + 1))
    return sum(1 for day in all_days if day.weekday() < 5)  # 0=Δευτέρα ... 4=Παρασκευή
