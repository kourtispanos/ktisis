from typing import Optional

from pydantic import BaseModel


class ClientIn(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class ProjectIn(BaseModel):
    name: str
    client_id: Optional[int] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None


class WorkerIn(BaseModel):
    name: str
    specialty: Optional[str] = None
    daily_wage: Optional[float] = None


class WageEntryIn(BaseModel):
    worker_id: int
    project_id: int
    work_date: str
    days: float
    amount: float


class ExpenseIn(BaseModel):
    project_id: int
    amount: float
    expense_date: str
    category: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class IncomeIn(BaseModel):
    project_id: int
    amount: float
    income_date: str
    client_id: Optional[int] = None
    description: Optional[str] = None
    vat_rate: Optional[float] = 24.0


class InvoiceIn(BaseModel):
    invoice_number: Optional[str] = None
    project_id: int
    amount: float
    invoice_date: str
    vat_rate: Optional[float] = 24.0
    paid: int = 0
    notes: Optional[str] = None


class TaxIn(BaseModel):
    tax_type: str
    amount: float
    due_date: str
    paid: int = 0


class EventIn(BaseModel):
    event_date: str
    title: str
    event_type: Optional[str] = None
    notes: Optional[str] = None


class VehicleIn(BaseModel):
    name: str
    license_plate: Optional[str] = None
    insurance_expiry: Optional[str] = None
    kteo_expiry: Optional[str] = None
    road_tax_expiry: Optional[str] = None
    last_service_date: Optional[str] = None
    service_notes: Optional[str] = None
    notes: Optional[str] = None


class Credentials(BaseModel):
    username: str
    password: str


class PasswordIn(BaseModel):
    password: str
