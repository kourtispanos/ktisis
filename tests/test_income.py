import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))

from base import DBTestCase
from backend.services.people import add_client
from backend.services.finance import add_income, get_total_vat_reserve
from backend.services.projects import add_project


class TestVatReserve(DBTestCase):
    def setUp(self):
        super().setUp()
        add_client("Πελάτης")
        add_project("Έργο", client_id=1)

    def test_default_24_percent(self):
        add_income(project_id=1, amount=1000.0, income_date="2026-09-10")
        self.assertEqual(get_total_vat_reserve(), 240.0)

    def test_reduced_13_percent(self):
        add_income(project_id=1, amount=1000.0, income_date="2026-09-10", vat_rate=13.0)
        self.assertEqual(get_total_vat_reserve(), 130.0)

    def test_multiple_entries_sum(self):
        add_income(project_id=1, amount=1000.0, income_date="2026-09-10", vat_rate=24.0)
        add_income(project_id=1, amount=500.0, income_date="2026-09-11", vat_rate=13.0)
        self.assertEqual(get_total_vat_reserve(), 240.0 + 65.0)


if __name__ == "__main__":
    unittest.main()
