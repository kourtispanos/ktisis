import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))
from db import get_connection


def _sum_where_month(table, amount_column, date_column, year, month):
    period = f"{year:04d}-{month:02d}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT COALESCE(SUM({amount_column}), 0) FROM {table} WHERE strftime('%Y-%m', {date_column}) = ?",
        (period,)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def _sum_vat_where_month(year, month):
    period = f"{year:04d}-{month:02d}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT COALESCE(SUM(amount * COALESCE(vat_rate, 0) / 100), 0)
           FROM income WHERE strftime('%Y-%m', income_date) = ?""",
        (period,)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_monthly_report(year, month):
    turnover = _sum_where_month("income", "amount", "income_date", year, month)
    expenses_total = _sum_where_month("expenses", "amount", "expense_date", year, month)
    wages_total = _sum_where_month("wage_entries", "amount", "work_date", year, month)
    vat_due = _sum_vat_where_month(year, month)
    other_taxes = _sum_where_month("taxes", "amount", "due_date", year, month)

    net_profit = turnover - expenses_total - wages_total - vat_due - other_taxes
    profit_margin_pct = (net_profit / turnover * 100) if turnover else 0.0

    return {
        "year": year,
        "month": month,
        "turnover": turnover,
        "expenses_total": expenses_total,
        "wages_total": wages_total,
        "vat_due": vat_due,
        "other_taxes": other_taxes,
        "net_profit": net_profit,
        "profit_margin_pct": profit_margin_pct,
    }


def get_yearly_report(year):
    months = [get_monthly_report(year, m) for m in range(1, 13)]

    totals = {
        "year": year,
        "turnover": sum(m["turnover"] for m in months),
        "expenses_total": sum(m["expenses_total"] for m in months),
        "wages_total": sum(m["wages_total"] for m in months),
        "vat_due": sum(m["vat_due"] for m in months),
        "other_taxes": sum(m["other_taxes"] for m in months),
    }
    totals["net_profit"] = (
        totals["turnover"] - totals["expenses_total"] - totals["wages_total"]
        - totals["vat_due"] - totals["other_taxes"]
    )
    totals["profit_margin_pct"] = (
        totals["net_profit"] / totals["turnover"] * 100 if totals["turnover"] else 0.0
    )
    return totals, months


def get_expense_breakdown_by_category(year):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT category, COALESCE(SUM(amount), 0) AS total
           FROM expenses
           WHERE strftime('%Y', expense_date) = ?
           GROUP BY category
           ORDER BY total DESC""",
        (str(year),)
    )
    rows = cursor.fetchall()
    conn.close()

    grand_total = sum(row[1] for row in rows) or 1
    return [
        (category or "Χωρίς κατηγορία", amount, amount / grand_total * 100)
        for category, amount in rows
    ]
