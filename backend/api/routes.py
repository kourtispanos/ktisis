from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.api import schemas
from backend.api.crud import make_crud_router, rows_to_dicts
from backend.api.deps import create_session, end_session, end_user_sessions, get_token, require_auth
from backend.auth.users import add_user, check_login, delete_user
from backend.external.weather import get_current_weather, get_forecast, get_weather_emoji
from backend.services import calendar_events, finance, people, projects, reports, vehicles

api = APIRouter(prefix="/api")

# ---------- Σύνδεση / Εγγραφή (χωρίς έλεγχο token) ----------
auth_router = APIRouter(prefix="/auth")


@auth_router.post("/login")
def login(credentials: schemas.Credentials):
    if not check_login(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Λάθος όνομα χρήστη ή κωδικός")
    return {"token": create_session(credentials.username), "username": credentials.username}


@auth_router.post("/signup", status_code=201)
def signup(credentials: schemas.Credentials):
    if not credentials.username or not credentials.password:
        raise HTTPException(status_code=400, detail="Συμπλήρωσε όνομα χρήστη και κωδικό")
    if not add_user(credentials.username, credentials.password):
        raise HTTPException(status_code=409, detail="Αυτό το όνομα χρήστη υπάρχει ήδη")
    return {"ok": True}


@auth_router.post("/logout")
def logout(token: str = Depends(get_token)):
    end_session(token)
    return {"ok": True}


@auth_router.get("/me")
def me(username: str = Depends(require_auth)):
    return {"username": username}


@auth_router.post("/delete-account")
def delete_account(confirmation: schemas.PasswordIn, username: str = Depends(require_auth)):
    if not delete_user(username, confirmation.password):
        raise HTTPException(status_code=403, detail="Λάθος κωδικός")
    end_user_sessions(username)
    return {"ok": True}


api.include_router(auth_router)

# ---------- Στατικές λίστες για τις φόρμες ----------
meta_router = APIRouter(prefix="/meta", dependencies=[Depends(require_auth)])


@meta_router.get("")
def get_meta():
    return {
        "expense_categories": finance.EXPENSE_CATEGORIES,
        "event_types": calendar_events.EVENT_TYPES,
        "default_vat_rate": finance.DEFAULT_VAT_RATE,
    }


api.include_router(meta_router)

# ---------- Απλό CRUD ανά οντότητα ----------
api.include_router(make_crud_router(
    "/clients", "clients", schemas.ClientIn,
    people.list_clients, people.add_client, people.update_client, people.delete_client))


def add_working_days(project):
    # Εργάσιμες μέρες υπολογίζονται μόνο για ολοκληρωμένα έργα με γνωστές ημερομηνίες
    if project["status"] == "ολοκληρωμένο":
        project["working_days"] = projects.calculate_working_days(project["start_date"], project["end_date"])
    else:
        project["working_days"] = None


api.include_router(make_crud_router(
    "/projects", "projects", schemas.ProjectIn,
    projects.list_projects, projects.add_project, projects.update_project, projects.delete_project,
    enrich=add_working_days))
api.include_router(make_crud_router(
    "/workers", "workers", schemas.WorkerIn,
    people.list_workers, people.add_worker, people.update_worker, people.delete_worker))
api.include_router(make_crud_router(
    "/wage-entries", "wage_entries", schemas.WageEntryIn,
    people.list_wage_entries, people.add_wage_entry,
    people.update_wage_entry, people.delete_wage_entry))
api.include_router(make_crud_router(
    "/expenses", "expenses", schemas.ExpenseIn,
    finance.list_expenses, finance.add_expense, finance.update_expense, finance.delete_expense))
api.include_router(make_crud_router(
    "/income", "income", schemas.IncomeIn,
    finance.list_income, finance.add_income, finance.update_income, finance.delete_income))
api.include_router(make_crud_router(
    "/invoices", "invoices", schemas.InvoiceIn,
    finance.list_invoices, finance.add_invoice, finance.update_invoice, finance.delete_invoice))
api.include_router(make_crud_router(
    "/taxes", "taxes", schemas.TaxIn,
    finance.list_taxes, finance.add_tax, finance.update_tax, finance.delete_tax))
api.include_router(make_crud_router(
    "/events", "calendar_events", schemas.EventIn,
    calendar_events.list_events, calendar_events.add_event,
    calendar_events.update_event, calendar_events.delete_event))
api.include_router(make_crud_router(
    "/vehicles", "vehicles", schemas.VehicleIn,
    vehicles.list_vehicles_with_status, vehicles.add_vehicle,
    vehicles.update_vehicle, vehicles.delete_vehicle,
    extra_columns=("insurance_status", "kteo_status", "road_tax_status")))

# ---------- Υπολογισμοί / συγκεντρωτικά ----------
stats = APIRouter(dependencies=[Depends(require_auth)])


@stats.get("/clients/balances/all")
def client_balances():
    keys = ("id", "name", "total_budget", "total_paid", "balance")
    return [dict(zip(keys, row)) for row in people.get_client_balances()]


@stats.get("/projects/financials/all")
def project_financials():
    return projects.get_project_financials()


@stats.get("/workers/totals/all")
def worker_totals():
    keys = ("id", "name", "specialty", "daily_wage", "total_days", "total_amount")
    return [dict(zip(keys, row)) for row in people.get_worker_totals()]


@stats.get("/income/vat-reserve")
def vat_reserve():
    return {"total": finance.get_total_vat_reserve()}


@stats.get("/invoices/unpaid-total")
def unpaid_total():
    return {"total": finance.get_total_unpaid()}


@stats.get("/events/upcoming/all")
def upcoming_events():
    return rows_to_dicts("calendar_events", calendar_events.get_upcoming_events(), ("status",))


@stats.get("/reports/monthly")
def monthly_report(year: int, month: int, project_id: Optional[int] = None):
    return reports.get_monthly_report(year, month, project_id)


@stats.get("/reports/yearly")
def yearly_report(year: int, project_id: Optional[int] = None):
    totals, months = reports.get_yearly_report(year, project_id)
    return {"totals": totals, "months": months}


@stats.get("/reports/expense-breakdown")
def expense_breakdown(year: int, project_id: Optional[int] = None):
    return [
        {"category": category, "amount": amount, "percent": percent}
        for category, amount, percent in reports.get_expense_breakdown_by_category(year, project_id)
    ]


@stats.get("/weather")
def weather(city: str):
    current = get_current_weather(city)
    forecast = get_forecast(city)
    if current is None:
        raise HTTPException(
            status_code=503,
            detail="Ο καιρός δεν είναι διαθέσιμος (έλεγξε το API key, την πόλη ή τη σύνδεση στο internet)",
        )
    current["emoji"] = get_weather_emoji(current["main"])
    for day in forecast or []:
        day["emoji"] = get_weather_emoji(day["main"])
    return {"current": current, "forecast": forecast or []}


api.include_router(stats)
