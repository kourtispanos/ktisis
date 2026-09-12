import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

EVENT_TYPES = ["Ραντεβού", "Σέρβις οχήματος", "Προθεσμία", "Άλλο"]
UPCOMING_DAYS = 7


def add_event(event_date, title, event_type=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO calendar_events (event_date, title, event_type, notes) VALUES (?, ?, ?, ?)",
        (event_date, title, event_type, notes)
    )

    conn.commit()
    conn.close()


def update_event(event_id, event_date, title, event_type=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE calendar_events SET event_date = ?, title = ?, event_type = ?, notes = ? WHERE id = ?",
        (event_date, title, event_type, notes, event_id)
    )

    conn.commit()
    conn.close()


def delete_event(event_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))

    conn.commit()
    conn.close()


def list_events():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM calendar_events ORDER BY event_date")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_upcoming_events():
    today = datetime.date.today()
    result = []
    for e in list_events():
        event_date = datetime.date.fromisoformat(e[1])
        days_left = (event_date - today).days
        if days_left < 0:
            status = "Πέρασε"
        elif days_left == 0:
            status = "Σήμερα"
        elif days_left <= UPCOMING_DAYS:
            status = "Σύντομα"
        else:
            continue
        result.append(e + (status,))
    return result
