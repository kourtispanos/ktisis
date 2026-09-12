import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))

from base import DBTestCase
from clients import add_client, get_client_balances
from income import add_income
from projects import add_project


class TestClientBalances(DBTestCase):
    def test_balance_with_no_income(self):
        add_client("Πελάτης Α")
        add_project("Έργο 1", client_id=1, budget=5000.0)

        _, _, budget, paid, balance = get_client_balances()[0]
        self.assertEqual(budget, 5000.0)
        self.assertEqual(paid, 0)
        self.assertEqual(balance, 5000.0)

    def test_balance_after_partial_payment(self):
        add_client("Πελάτης Β")
        add_project("Έργο 2", client_id=1, budget=2000.0)
        add_income(project_id=1, amount=800.0, income_date="2026-09-10", client_id=1)

        _, _, budget, paid, balance = get_client_balances()[0]
        self.assertEqual(budget, 2000.0)
        self.assertEqual(paid, 800.0)
        self.assertEqual(balance, 1200.0)


if __name__ == "__main__":
    unittest.main()
