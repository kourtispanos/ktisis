from backend.database.db import fetch_all, fetch_value

# Τα ποσά που αθροίζονται για να βγει το σύνολο ενός έτους
SUMMED_FIELDS = ("turnover", "expenses_total", "wages_total", "vat_due", "other_taxes")


def _sum_for_month(table, amount_column, date_column, year, month, project_id=None):
    query = f"SELECT COALESCE(SUM({amount_column}), 0) FROM {table} WHERE strftime('%Y-%m', {date_column}) = ?"
    params = [f"{year:04d}-{month:02d}"]
    if project_id is not None:
        query += " AND project_id = ?"
        params.append(project_id)
    return fetch_value(query, tuple(params))


def _vat_for_month(year, month, project_id=None):
    query = """SELECT COALESCE(SUM(amount * COALESCE(vat_rate, 0) / 100), 0)
               FROM income WHERE strftime('%Y-%m', income_date) = ?"""
    params = [f"{year:04d}-{month:02d}"]
    if project_id is not None:
        query += " AND project_id = ?"
        params.append(project_id)
    return fetch_value(query, tuple(params))


def _add_profit(figures):
    """Προσθέτει καθαρά κέρδη και περιθώριο κέρδους σε ένα λεξικό με τα ποσά μιας περιόδου."""
    figures["net_profit"] = (
        figures["turnover"] - figures["expenses_total"] - figures["wages_total"]
        - figures["vat_due"] - figures["other_taxes"]
    )
    figures["profit_margin_pct"] = (
        figures["net_profit"] / figures["turnover"] * 100 if figures["turnover"] else 0.0
    )
    return figures


def get_monthly_report(year, month, project_id=None):
    # Ο πίνακας taxes δεν συνδέεται με συγκεκριμένο έργο (είναι γενικές υποχρεώσεις
    # της επιχείρησης) - όταν φιλτράρουμε ανά έργο δεν έχει νόημα, μένει μηδέν.
    other_taxes = 0.0 if project_id is not None else _sum_for_month("taxes", "amount", "due_date", year, month)
    return _add_profit({
        "year": year,
        "month": month,
        "turnover": _sum_for_month("income", "amount", "income_date", year, month, project_id),
        "expenses_total": _sum_for_month("expenses", "amount", "expense_date", year, month, project_id),
        "wages_total": _sum_for_month("wage_entries", "amount", "work_date", year, month, project_id),
        "vat_due": _vat_for_month(year, month, project_id),
        "other_taxes": other_taxes,
    })


def get_yearly_report(year, project_id=None):
    """Επιστρέφει (σύνολα έτους, λίστα με τα 12 μηνιαία)."""
    months = [get_monthly_report(year, month, project_id) for month in range(1, 13)]
    totals = {"year": year, **{field: sum(m[field] for m in months) for field in SUMMED_FIELDS}}
    return _add_profit(totals), months


def get_expense_breakdown_by_category(year, project_id=None):
    query = """SELECT category, COALESCE(SUM(amount), 0) AS total
               FROM expenses
               WHERE strftime('%Y', expense_date) = ?"""
    params = [str(year)]
    if project_id is not None:
        query += " AND project_id = ?"
        params.append(project_id)
    query += " GROUP BY category ORDER BY total DESC"

    rows = fetch_all(query, tuple(params))
    grand_total = sum(amount for _, amount in rows) or 1
    return [
        (category or "Χωρίς κατηγορία", amount, amount / grand_total * 100)
        for category, amount in rows
    ]
