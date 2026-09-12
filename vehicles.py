import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection

WARNING_DAYS = 7


def add_vehicle(
    name, license_plate=None, insurance_expiry=None, kteo_expiry=None,
    road_tax_expiry=None, last_service_date=None, service_notes=None, notes=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO vehicles
           (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
            last_service_date, service_notes, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
         last_service_date, service_notes, notes)
    )

    conn.commit()
    conn.close()


def update_vehicle(
    vehicle_id, name, license_plate=None, insurance_expiry=None, kteo_expiry=None,
    road_tax_expiry=None, last_service_date=None, service_notes=None, notes=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """UPDATE vehicles
           SET name = ?, license_plate = ?, insurance_expiry = ?, kteo_expiry = ?,
               road_tax_expiry = ?, last_service_date = ?, service_notes = ?, notes = ?
           WHERE id = ?""",
        (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
         last_service_date, service_notes, notes, vehicle_id)
    )

    conn.commit()
    conn.close()


def delete_vehicle(vehicle_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))

    conn.commit()
    conn.close()


def list_vehicles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicles")
    rows = cursor.fetchall()

    conn.close()
    return rows


def _status_for(expiry_str):
    if not expiry_str:
        return "-"
    expiry = datetime.date.fromisoformat(expiry_str)
    days_left = (expiry - datetime.date.today()).days
    if days_left < 0:
        return "Έληξε"
    if days_left <= WARNING_DAYS:
        return "Λήγει σύντομα"
    return "OK"


def list_vehicles_with_status():
    result = []
    for v in list_vehicles():
        insurance_status = _status_for(v[3])
        kteo_status = _status_for(v[4])
        road_tax_status = _status_for(v[5])
        result.append(v + (insurance_status, kteo_status, road_tax_status))
    return result
