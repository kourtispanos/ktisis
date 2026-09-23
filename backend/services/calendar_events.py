import datetime

from backend.database.db import delete_row, execute, fetch_all

EVENT_TYPES = ["Ραντεβού", "Σέρβις οχήματος", "Προθεσμία", "Άλλο"]
UPCOMING_DAYS = 7


def add_event(event_date, title, event_type=None, notes=None):
    execute(
        "INSERT INTO calendar_events (event_date, title, event_type, notes) VALUES (?, ?, ?, ?)",
        (event_date, title, event_type, notes),
    )


def update_event(event_id, event_date, title, event_type=None, notes=None):
    execute(
        "UPDATE calendar_events SET event_date = ?, title = ?, event_type = ?, notes = ? WHERE id = ?",
        (event_date, title, event_type, notes, event_id),
    )


def delete_event(event_id):
    return delete_row("calendar_events", event_id)


def list_events():
    return fetch_all("SELECT * FROM calendar_events ORDER BY event_date")


def _upcoming_status(days_left):
    """Κατάσταση υπενθύμισης, ή None αν είναι πολύ μακριά για να εμφανιστεί στα επερχόμενα."""
    if days_left < 0:
        return "Πέρασε"
    if days_left == 0:
        return "Σήμερα"
    if days_left <= UPCOMING_DAYS:
        return "Σύντομα"
    return None


def get_upcoming_events():
    """Υπενθυμίσεις που πέρασαν ή έρχονται σύντομα, με την κατάσταση στο τέλος κάθε γραμμής."""
    today = datetime.date.today()
    result = []
    for event in list_events():
        days_left = (datetime.date.fromisoformat(event[1]) - today).days
        status = _upcoming_status(days_left)
        if status:
            result.append(event + (status,))
    return result
