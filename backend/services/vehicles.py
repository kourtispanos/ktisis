import datetime

from backend.database.db import delete_row, execute, fetch_all

WARNING_DAYS = 7


def add_vehicle(
    name, license_plate=None, insurance_expiry=None, kteo_expiry=None,
    road_tax_expiry=None, last_service_date=None, service_notes=None, notes=None,
):
    execute(
        """INSERT INTO vehicles
           (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
            last_service_date, service_notes, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
         last_service_date, service_notes, notes),
    )


def update_vehicle(
    vehicle_id, name, license_plate=None, insurance_expiry=None, kteo_expiry=None,
    road_tax_expiry=None, last_service_date=None, service_notes=None, notes=None,
):
    execute(
        """UPDATE vehicles
           SET name = ?, license_plate = ?, insurance_expiry = ?, kteo_expiry = ?,
               road_tax_expiry = ?, last_service_date = ?, service_notes = ?, notes = ?
           WHERE id = ?""",
        (name, license_plate, insurance_expiry, kteo_expiry, road_tax_expiry,
         last_service_date, service_notes, notes, vehicle_id),
    )


def delete_vehicle(vehicle_id):
    return delete_row("vehicles", vehicle_id)


def list_vehicles():
    return fetch_all("SELECT * FROM vehicles")


def _status_for(expiry_str):
    if not expiry_str:
        return "-"
    days_left = (datetime.date.fromisoformat(expiry_str) - datetime.date.today()).days
    if days_left < 0:
        return "Έληξε"
    if days_left <= WARNING_DAYS:
        return "Λήγει σύντομα"
    return "OK"


def list_vehicles_with_status():
    """Κάθε όχημα με τρεις επιπλέον τιμές στο τέλος: κατάσταση ασφάλειας, ΚΤΕΟ, τελών κυκλοφορίας."""
    result = []
    for vehicle in list_vehicles():
        _, _, _, insurance_expiry, kteo_expiry, road_tax_expiry, *_ = vehicle
        statuses = (_status_for(insurance_expiry), _status_for(kteo_expiry), _status_for(road_tax_expiry))
        result.append(vehicle + statuses)
    return result
