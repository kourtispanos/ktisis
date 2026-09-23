import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))

from base import DBTestCase
from backend.services.people import add_client
from backend.services.finance import add_expense
from backend.services.projects import add_project, calculate_working_days, get_project_financials
from backend.services.people import add_wage_entry, add_worker


class TestCalculateWorkingDays(unittest.TestCase):
    def test_full_week(self):
        self.assertEqual(calculate_working_days("2026-09-07", "2026-09-11"), 5)

    def test_includes_weekend(self):
        self.assertEqual(calculate_working_days("2026-09-07", "2026-09-14"), 6)

    def test_missing_dates_returns_none(self):
        self.assertIsNone(calculate_working_days(None, "2026-09-11"))
        self.assertIsNone(calculate_working_days("2026-09-11", None))

    def test_end_before_start_returns_none(self):
        self.assertIsNone(calculate_working_days("2026-09-11", "2026-09-07"))


class TestProjectFinancials(DBTestCase):
    def test_spent_and_remaining(self):
        add_client("Test Client")
        add_project("Test Project", client_id=1, budget=1000.0)
        add_expense(project_id=1, amount=300.0, expense_date="2026-09-10")
        add_worker("Test Worker", daily_wage=100.0)
        add_wage_entry(worker_id=1, project_id=1, work_date="2026-09-10", days=2, amount=200.0)

        pf = get_project_financials()[0]
        self.assertEqual(pf["expenses"], 300.0)
        self.assertEqual(pf["wages"], 200.0)
        self.assertEqual(pf["spent"], 500.0)
        self.assertEqual(pf["remaining"], 500.0)
        self.assertEqual(pf["spent_pct"], 50.0)

    def test_no_budget_gives_none_percentages(self):
        add_client("Test Client")
        add_project("No Budget Project", client_id=1)

        pf = get_project_financials()[0]
        self.assertIsNone(pf["spent_pct"])
        self.assertIsNone(pf["remaining"])


if __name__ == "__main__":
    unittest.main()
