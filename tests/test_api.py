import unittest

from fastapi.testclient import TestClient

from base import DBTestCase
from backend.main import app


class APITestCase(DBTestCase):
    def setUp(self):
        super().setUp()
        self.client = TestClient(app)
        self.client.post("/api/auth/signup", json={"username": "tester", "password": "secret"})
        token = self.client.post(
            "/api/auth/login", json={"username": "tester", "password": "secret"}
        ).json()["token"]
        self.headers = {"Authorization": f"Bearer {token}"}


class TestAuth(APITestCase):
    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/clients").status_code, 401)

    def test_wrong_password_rejected(self):
        response = self.client.post("/api/auth/login", json={"username": "tester", "password": "nope"})
        self.assertEqual(response.status_code, 401)

    def test_duplicate_signup_conflict(self):
        response = self.client.post("/api/auth/signup", json={"username": "tester", "password": "x"})
        self.assertEqual(response.status_code, 409)


class TestDeleteAccount(APITestCase):
    def test_wrong_password_keeps_account(self):
        response = self.client.post("/api/auth/delete-account", json={"password": "nope"}, headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get("/api/auth/me", headers=self.headers).status_code, 200)

    def test_delete_removes_account_and_sessions(self):
        response = self.client.post("/api/auth/delete-account", json={"password": "secret"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me", headers=self.headers).status_code, 401)
        login = self.client.post("/api/auth/login", json={"username": "tester", "password": "secret"})
        self.assertEqual(login.status_code, 401)

    def test_business_data_survives_account_deletion(self):
        self.client.post("/api/clients", json={"name": "Α"}, headers=self.headers)
        self.client.post("/api/auth/delete-account", json={"password": "secret"}, headers=self.headers)
        self.client.post("/api/auth/signup", json={"username": "other", "password": "x"})
        token = self.client.post("/api/auth/login", json={"username": "other", "password": "x"}).json()["token"]
        clients = self.client.get("/api/clients", headers={"Authorization": f"Bearer {token}"}).json()
        self.assertEqual(clients[0]["name"], "Α")

    def test_requires_login(self):
        self.assertEqual(self.client.post("/api/auth/delete-account", json={"password": "x"}).status_code, 401)


class TestCrud(APITestCase):
    def test_client_crud_cycle(self):
        h = self.headers
        self.client.post("/api/clients", json={"name": "Γιάννης", "phone": "123"}, headers=h)
        rows = self.client.get("/api/clients", headers=h).json()
        self.assertEqual(rows[0]["name"], "Γιάννης")
        cid = rows[0]["id"]

        self.client.put(f"/api/clients/{cid}", json={"name": "Νίκος"}, headers=h)
        self.assertEqual(self.client.get("/api/clients", headers=h).json()[0]["name"], "Νίκος")

        self.assertEqual(self.client.delete(f"/api/clients/{cid}", headers=h).status_code, 200)
        self.assertEqual(self.client.get("/api/clients", headers=h).json(), [])

    def test_delete_client_with_project_is_conflict(self):
        h = self.headers
        self.client.post("/api/clients", json={"name": "Α"}, headers=h)
        cid = self.client.get("/api/clients", headers=h).json()[0]["id"]
        self.client.post("/api/projects", json={"name": "Έργο", "client_id": cid}, headers=h)
        self.assertEqual(self.client.delete(f"/api/clients/{cid}", headers=h).status_code, 409)

    def test_project_financials_and_balances(self):
        h = self.headers
        self.client.post("/api/clients", json={"name": "Α"}, headers=h)
        cid = self.client.get("/api/clients", headers=h).json()[0]["id"]
        self.client.post("/api/projects", json={"name": "Έργο", "client_id": cid, "budget": 1000}, headers=h)
        pid = self.client.get("/api/projects", headers=h).json()[0]["id"]
        self.client.post("/api/expenses", json={
            "project_id": pid, "amount": 250, "expense_date": "2026-01-10"}, headers=h)
        self.client.post("/api/income", json={
            "project_id": pid, "client_id": cid, "amount": 400, "income_date": "2026-01-15"}, headers=h)

        financials = self.client.get("/api/projects/financials/all", headers=h).json()[0]
        self.assertEqual(financials["spent"], 250)
        self.assertEqual(financials["remaining"], 750)

        balance = self.client.get("/api/clients/balances/all", headers=h).json()[0]
        self.assertEqual(balance["balance"], 600)

    def test_vehicle_status_included(self):
        h = self.headers
        self.client.post("/api/vehicles", json={"name": "Φορτηγό", "kteo_expiry": "2000-01-01"}, headers=h)
        vehicle = self.client.get("/api/vehicles", headers=h).json()[0]
        self.assertEqual(vehicle["kteo_status"], "Έληξε")

    def test_monthly_report(self):
        h = self.headers
        self.client.post("/api/clients", json={"name": "Α"}, headers=h)
        self.client.post("/api/projects", json={"name": "Έργο"}, headers=h)
        pid = self.client.get("/api/projects", headers=h).json()[0]["id"]
        self.client.post("/api/income", json={
            "project_id": pid, "amount": 1000, "income_date": "2026-03-05", "vat_rate": 24}, headers=h)
        report = self.client.get("/api/reports/monthly?year=2026&month=3", headers=h).json()
        self.assertEqual(report["turnover"], 1000)
        self.assertEqual(report["vat_due"], 240)

    def test_monthly_report_filtered_by_project(self):
        h = self.headers
        self.client.post("/api/projects", json={"name": "Α"}, headers=h)
        self.client.post("/api/projects", json={"name": "Β"}, headers=h)
        pid_a, pid_b = (p["id"] for p in self.client.get("/api/projects", headers=h).json())
        self.client.post("/api/income", json={
            "project_id": pid_a, "amount": 1000, "income_date": "2026-03-05", "vat_rate": 24}, headers=h)
        self.client.post("/api/income", json={
            "project_id": pid_b, "amount": 500, "income_date": "2026-03-05", "vat_rate": 24}, headers=h)
        self.client.post("/api/taxes", json={"tax_type": "Φόρος", "amount": 300, "due_date": "2026-03-01"}, headers=h)

        combined = self.client.get("/api/reports/monthly?year=2026&month=3", headers=h).json()
        self.assertEqual(combined["turnover"], 1500)
        self.assertEqual(combined["other_taxes"], 300)

        only_a = self.client.get(f"/api/reports/monthly?year=2026&month=3&project_id={pid_a}", headers=h).json()
        self.assertEqual(only_a["turnover"], 1000)
        self.assertEqual(only_a["vat_due"], 240)
        # Οι γενικές φορολογίες δεν ανήκουν σε συγκεκριμένο έργο
        self.assertEqual(only_a["other_taxes"], 0)

    def test_expense_breakdown_filtered_by_project(self):
        h = self.headers
        self.client.post("/api/projects", json={"name": "Α"}, headers=h)
        self.client.post("/api/projects", json={"name": "Β"}, headers=h)
        pid_a, pid_b = (p["id"] for p in self.client.get("/api/projects", headers=h).json())
        self.client.post("/api/expenses", json={
            "project_id": pid_a, "amount": 200, "expense_date": "2026-03-05", "category": "Ξυλεία"}, headers=h)
        self.client.post("/api/expenses", json={
            "project_id": pid_b, "amount": 800, "expense_date": "2026-03-05", "category": "Ξυλεία"}, headers=h)

        breakdown = self.client.get(f"/api/reports/expense-breakdown?year=2026&project_id={pid_a}", headers=h).json()
        self.assertEqual(breakdown, [{"category": "Ξυλεία", "amount": 200, "percent": 100.0}])


if __name__ == "__main__":
    unittest.main()
