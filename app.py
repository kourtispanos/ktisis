import calendar
import datetime

import streamlit as st

from clients import add_client, update_client, delete_client, list_clients, get_client_balances
from projects import (
    add_project, update_project, delete_project, list_projects,
    calculate_working_days, get_project_financials
)
from workers import add_worker, update_worker, delete_worker, list_workers, get_worker_totals
from wage_entries import add_wage_entry, update_wage_entry, delete_wage_entry, list_wage_entries
from expenses import add_expense, update_expense, delete_expense, list_expenses, EXPENSE_CATEGORIES
from income import add_income, update_income, delete_income, list_income, get_total_vat_reserve
from taxes import add_tax, update_tax, delete_tax, list_taxes
from calendar_events import add_event, update_event, delete_event, list_events, get_upcoming_events, EVENT_TYPES
from weather import get_current_weather, get_forecast, get_weather_emoji
from vehicles import add_vehicle, update_vehicle, delete_vehicle, list_vehicles, list_vehicles_with_status
from reports import get_monthly_report, get_yearly_report, get_expense_breakdown_by_category
from invoices import add_invoice, update_invoice, delete_invoice, list_invoices, get_total_unpaid
from users import add_user, check_login
from create_db import create_tables

create_tables()

st.set_page_config(page_title="Ktisis", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.authenticated:
    st.title("Ktisis")
    tab_login, tab_signup = st.tabs(["Σύνδεση", "Εγγραφή"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Όνομα χρήστη")
            password = st.text_input("Κωδικός", type="password")
            if st.form_submit_button("Σύνδεση"):
                if check_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Λάθος όνομα χρήστη ή κωδικός")

    with tab_signup:
        with st.form("signup_form", clear_on_submit=True):
            new_username = st.text_input("Όνομα χρήστη", key="signup_username")
            new_password = st.text_input("Κωδικός", type="password", key="signup_password")
            confirm_password = st.text_input("Επιβεβαίωση κωδικού", type="password", key="signup_confirm")
            if st.form_submit_button("Δημιουργία λογαριασμού"):
                if not new_username or not new_password:
                    st.error("Συμπλήρωσε όνομα χρήστη και κωδικό")
                elif new_password != confirm_password:
                    st.error("Οι κωδικοί δεν ταιριάζουν")
                elif add_user(new_username, new_password):
                    st.success("Ο λογαριασμός δημιουργήθηκε! Πήγαινε στο 'Σύνδεση' για να μπεις.")
                else:
                    st.error("Αυτό το όνομα χρήστη υπάρχει ήδη")

    st.stop()

with st.sidebar:
    st.write(f"Συνδεδεμένος ως **{st.session_state.username}**")
    if st.button("Αποσύνδεση"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

st.title("Ktisis - Διαχείριση Εργολαβίας")


def select_row(rows, format_func, key):
    if not rows:
        return None
    options = {row[0]: format_func(row) for row in rows}
    selected_id = st.selectbox(
        "Επίλεξε εγγραφή", options=list(options.keys()),
        format_func=lambda x: options[x], key=key
    )
    return next(row for row in rows if row[0] == selected_id)


(
    tab_clients, tab_projects, tab_staff, tab_finance, tab_taxes,
    tab_weather, tab_calendar, tab_vehicles, tab_reports
) = st.tabs([
    "Πελάτες", "Έργα", "Προσωπικό & Ημερομίσθια", "Έξοδα & Έσοδα", "Φορολογίες",
    "Καιρός", "Ημερολόγιο", "Οχήματα", "Αναφορές"
])

# ---------------------------------------------------------------- Πελάτες
with tab_clients:
    st.subheader("Νέος πελάτης")
    with st.form("add_client_form", clear_on_submit=True):
        name = st.text_input("Όνομα")
        phone = st.text_input("Τηλέφωνο")
        email = st.text_input("Email")
        address = st.text_input("Διεύθυνση")
        if st.form_submit_button("Προσθήκη"):
            if name:
                add_client(name, phone or None, email or None, address or None)
                st.rerun()
            else:
                st.error("Το όνομα είναι υποχρεωτικό")

    st.subheader("Πελάτες - Πληρωμές & Υπόλοιπο")
    st.table([
        {
            "Πελάτης": name,
            "Προϋπολογισμός έργων": f"{budget:.2f} €",
            "Πληρωμένο": f"{paid:.2f} €",
            "Υπόλοιπο": f"{balance:.2f} €",
        }
        for (_, name, budget, paid, balance) in get_client_balances()
    ])

    st.subheader("Επεξεργασία / Διαγραφή πελάτη")
    selected = select_row(list_clients(), lambda c: c[1], key="edit_client_select")
    if selected is None:
        st.info("Δεν υπάρχουν πελάτες ακόμα.")
    else:
        with st.form("edit_client_form"):
            name = st.text_input("Όνομα", value=selected[1])
            phone = st.text_input("Τηλέφωνο", value=selected[2] or "")
            email = st.text_input("Email", value=selected[3] or "")
            address = st.text_input("Διεύθυνση", value=selected[4] or "")
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                update_client(selected[0], name, phone or None, email or None, address or None)
                st.rerun()
            if delete_clicked:
                if delete_client(selected[0]):
                    st.rerun()
                else:
                    st.error("Δεν μπορείς να διαγράψεις - ο πελάτης έχει συνδεδεμένα έργα ή έσοδα.")

# ----------------------------------------------------------------- Έργα
with tab_projects:
    st.subheader("Νέο έργο")
    clients_data = list_clients()
    if not clients_data:
        st.warning("Πρόσθεσε πρώτα έναν πελάτη.")
    else:
        client_options = {c[0]: c[1] for c in clients_data}
        with st.form("add_project_form", clear_on_submit=True):
            name = st.text_input("Όνομα έργου")
            client_id = st.selectbox(
                "Πελάτης", options=list(client_options.keys()),
                format_func=lambda x: client_options[x]
            )
            location = st.text_input("Τοποθεσία (πόλη)")
            start_date = st.date_input("Ημερομηνία έναρξης", value=datetime.date.today())
            status = st.selectbox("Κατάσταση", ["ενεργό", "σε παύση", "ολοκληρωμένο"])
            budget = st.number_input("Προϋπολογισμός (€)", min_value=0.0, step=100.0)
            has_end_date = st.checkbox("Έχει ολοκληρωθεί με γνωστή ημερομηνία;")
            end_date = st.date_input("Ημερομηνία ολοκλήρωσης", value=datetime.date.today(), key="new_end_date")
            if st.form_submit_button("Προσθήκη"):
                if name:
                    add_project(
                        name, client_id, location or None, start_date.isoformat(), status, budget,
                        end_date.isoformat() if has_end_date else None
                    )
                    st.rerun()
                else:
                    st.error("Το όνομα είναι υποχρεωτικό")

    st.subheader("Έργα")
    client_names = {c[0]: c[1] for c in list_clients()}
    st.table([
        {
            "Όνομα": p[1],
            "Πελάτης": client_names.get(p[2], "-"),
            "Τοποθεσία": p[3],
            "Έναρξη": p[4],
            "Κατάσταση": p[5],
            "Προϋπολογισμός": f"{p[6]:.2f} €" if p[6] is not None else "-",
            "Ολοκλήρωση": p[7] or "-",
            "Εργάσιμες μέρες": (
                calculate_working_days(p[4], p[7])
                if p[5] == "ολοκληρωμένο" and calculate_working_days(p[4], p[7]) is not None
                else "-"
            ),
        }
        for p in list_projects()
    ])

    st.subheader("Ζωντανός προϋπολογισμός ανά έργο")
    financials = get_project_financials()
    if not financials:
        st.info("Δεν υπάρχουν έργα ακόμα.")
    else:
        for pf in financials:
            st.write(f"**{pf['name']}**")
            if pf["budget"]:
                progress_value = min(pf["spent_pct"] / 100, 1.0)
                st.progress(
                    progress_value,
                    text=f"{pf['spent']:.2f} € / {pf['budget']:.2f} € ({pf['spent_pct']:.1f}%)"
                )
                if pf["spent_pct"] > 100:
                    st.error(f"⚠️ Υπέρβαση προϋπολογισμού κατά {-pf['remaining']:.2f} €")
                else:
                    st.caption(f"Υπόλοιπο προϋπολογισμού: {pf['remaining']:.2f} €")
            else:
                st.caption("Δεν έχει οριστεί προϋπολογισμός για αυτό το έργο.")
            st.caption(
                f"Έξοδα: {pf['expenses']:.2f} € · Ημερομίσθια: {pf['wages']:.2f} € · "
                f"Έσοδα εισπραχθέντα: {pf['income']:.2f} €"
            )
            st.write("")

    st.subheader("Επεξεργασία / Διαγραφή έργου")
    projects_data = list_projects()
    selected = select_row(projects_data, lambda p: p[1], key="edit_project_select")
    if selected is None:
        st.info("Δεν υπάρχουν έργα ακόμα.")
    elif not clients_data:
        st.warning("Πρόσθεσε πρώτα έναν πελάτη.")
    else:
        with st.form("edit_project_form"):
            name = st.text_input("Όνομα έργου", value=selected[1])
            client_ids = list(client_options.keys())
            client_id = st.selectbox(
                "Πελάτης", options=client_ids,
                format_func=lambda x: client_options[x],
                index=client_ids.index(selected[2]) if selected[2] in client_ids else 0
            )
            location = st.text_input("Τοποθεσία (πόλη)", value=selected[3] or "")
            start_date = st.date_input(
                "Ημερομηνία έναρξης",
                value=datetime.date.fromisoformat(selected[4]) if selected[4] else datetime.date.today()
            )
            statuses = ["ενεργό", "σε παύση", "ολοκληρωμένο"]
            status = st.selectbox(
                "Κατάσταση", statuses,
                index=statuses.index(selected[5]) if selected[5] in statuses else 0
            )
            budget = st.number_input("Προϋπολογισμός (€)", min_value=0.0, step=100.0, value=selected[6] or 0.0)
            has_end_date = st.checkbox("Έχει ολοκληρωθεί με γνωστή ημερομηνία;", value=bool(selected[7]))
            end_date = st.date_input(
                "Ημερομηνία ολοκλήρωσης",
                value=datetime.date.fromisoformat(selected[7]) if selected[7] else datetime.date.today(),
                key="edit_end_date"
            )
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                if name:
                    update_project(
                        selected[0], name, client_id, location or None, start_date.isoformat(), status, budget,
                        end_date.isoformat() if has_end_date else None
                    )
                    st.rerun()
                else:
                    st.error("Το όνομα είναι υποχρεωτικό")
            if delete_clicked:
                if delete_project(selected[0]):
                    st.rerun()
                else:
                    st.error("Δεν μπορείς να διαγράψεις - το έργο έχει συνδεδεμένα ημερομίσθια/έξοδα/έσοδα/ημερολόγιο.")

# --------------------------------------------- Προσωπικό & Ημερομίσθια
with tab_staff:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Νέος εργάτης")
        with st.form("add_worker_form", clear_on_submit=True):
            name = st.text_input("Όνομα εργάτη")
            specialty = st.text_input("Ειδικότητα")
            daily_wage = st.number_input("Ημερομίσθιο (€)", min_value=0.0, step=5.0)
            if st.form_submit_button("Προσθήκη"):
                if name:
                    add_worker(name, specialty or None, daily_wage)
                    st.rerun()
                else:
                    st.error("Το όνομα είναι υποχρεωτικό")

        workers_data = list_workers()
        st.write("Προσωπικό - σύνολα:")
        st.table([
            {
                "Όνομα": w[1],
                "Ειδικότητα": w[2],
                "Ημερομίσθιο": f"{w[3]:.2f} €" if w[3] is not None else "-",
                "Σύνολο ημερών εργασίας": w[4],
                "Σύνολο αμοιβής": f"{w[5]:.2f} €",
            }
            for w in get_worker_totals()
        ])

        st.write("Επεξεργασία / Διαγραφή εργάτη:")
        selected = select_row(workers_data, lambda w: w[1], key="edit_worker_select")
        if selected is None:
            st.info("Δεν υπάρχουν εργάτες ακόμα.")
        else:
            with st.form("edit_worker_form"):
                name = st.text_input("Όνομα εργάτη", value=selected[1], key="edit_worker_name")
                specialty = st.text_input("Ειδικότητα", value=selected[2] or "", key="edit_worker_specialty")
                daily_wage = st.number_input(
                    "Ημερομίσθιο (€)", min_value=0.0, step=5.0,
                    value=selected[3] or 0.0, key="edit_worker_wage"
                )
                col_a, col_b = st.columns(2)
                update_clicked = col_a.form_submit_button("Ενημέρωση")
                delete_clicked = col_b.form_submit_button("Διαγραφή")
                if update_clicked:
                    if name:
                        update_worker(selected[0], name, specialty or None, daily_wage)
                        st.rerun()
                    else:
                        st.error("Το όνομα είναι υποχρεωτικό")
                if delete_clicked:
                    if delete_worker(selected[0]):
                        st.rerun()
                    else:
                        st.error("Δεν μπορείς να διαγράψεις - ο εργάτης έχει συνδεδεμένα ημερομίσθια.")

    with col2:
        st.subheader("Νέο ημερομίσθιο")
        projects_data = list_projects()
        if not workers_data or not projects_data:
            st.warning("Χρειάζεσαι τουλάχιστον έναν εργάτη και ένα έργο.")
        else:
            worker_options = {w[0]: w[1] for w in workers_data}
            worker_wage_map = {w[0]: (w[3] or 0.0) for w in workers_data}
            project_options = {p[0]: p[1] for p in projects_data}
            with st.form("add_wage_form", clear_on_submit=True):
                worker_id = st.selectbox(
                    "Εργάτης", options=list(worker_options.keys()),
                    format_func=lambda x: worker_options[x]
                )
                project_id = st.selectbox(
                    "Έργο", options=list(project_options.keys()),
                    format_func=lambda x: project_options[x], key="wage_project"
                )
                work_date = st.date_input("Ημερομηνία", value=datetime.date.today(), key="wage_date")
                days = st.number_input("Ημέρες", min_value=0.0, value=1.0, step=0.5)
                st.caption("Το ποσό υπολογίζεται αυτόματα: ημερομίσθιο εργάτη × ημέρες")
                if st.form_submit_button("Προσθήκη"):
                    amount = worker_wage_map.get(worker_id, 0.0) * days
                    add_wage_entry(worker_id, project_id, work_date.isoformat(), days, amount)
                    st.rerun()

        worker_names = {w[0]: w[1] for w in list_workers()}
        project_names_staff = {p[0]: p[1] for p in list_projects()}
        wage_data = list_wage_entries()
        st.write("Ημερομίσθια:")
        st.table([
            {
                "Εργάτης": worker_names.get(e[1], "-"),
                "Έργο": project_names_staff.get(e[2], "-"),
                "Ημερομηνία": e[3],
                "Ημέρες": e[4],
                "Ποσό": f"{e[5]:.2f} €",
            }
            for e in wage_data
        ])

        st.write("Επεξεργασία / Διαγραφή ημερομισθίου:")
        selected = select_row(
            wage_data,
            lambda e: f"{e[3]} - {worker_names.get(e[1], '-')} - {project_names_staff.get(e[2], '-')}",
            key="edit_wage_select"
        )
        if selected is None:
            st.info("Δεν υπάρχουν ημερομίσθια ακόμα.")
        elif not workers_data or not projects_data:
            st.warning("Χρειάζεσαι τουλάχιστον έναν εργάτη και ένα έργο.")
        else:
            with st.form("edit_wage_form"):
                worker_ids = list(worker_options.keys())
                worker_id = st.selectbox(
                    "Εργάτης", options=worker_ids, format_func=lambda x: worker_options[x],
                    index=worker_ids.index(selected[1]) if selected[1] in worker_ids else 0,
                    key="edit_wage_worker"
                )
                project_ids = list(project_options.keys())
                project_id = st.selectbox(
                    "Έργο", options=project_ids, format_func=lambda x: project_options[x],
                    index=project_ids.index(selected[2]) if selected[2] in project_ids else 0,
                    key="edit_wage_project"
                )
                work_date = st.date_input(
                    "Ημερομηνία", value=datetime.date.fromisoformat(selected[3]), key="edit_wage_date"
                )
                days = st.number_input("Ημέρες", min_value=0.0, value=selected[4], step=0.5, key="edit_wage_days")
                st.caption("Το ποσό υπολογίζεται αυτόματα: ημερομίσθιο εργάτη × ημέρες")
                col_a, col_b = st.columns(2)
                update_clicked = col_a.form_submit_button("Ενημέρωση")
                delete_clicked = col_b.form_submit_button("Διαγραφή")
                if update_clicked:
                    amount = worker_wage_map.get(worker_id, 0.0) * days
                    update_wage_entry(selected[0], worker_id, project_id, work_date.isoformat(), days, amount)
                    st.rerun()
                if delete_clicked:
                    delete_wage_entry(selected[0])
                    st.rerun()

# ----------------------------------------------------------- Έξοδα & Έσοδα
with tab_finance:
    col1, col2 = st.columns(2)
    projects_data = list_projects()
    project_names = {p[0]: p[1] for p in projects_data}
    project_options = {p[0]: p[1] for p in projects_data}
    project_client_map = {p[0]: p[2] for p in projects_data}

    with col1:
        st.subheader("Νέο έξοδο")
        if not projects_data:
            st.warning("Πρόσθεσε πρώτα ένα έργο.")
        else:
            with st.form("add_expense_form", clear_on_submit=True):
                project_id = st.selectbox(
                    "Έργο", options=list(project_options.keys()),
                    format_func=lambda x: project_options[x], key="exp_project"
                )
                category = st.selectbox("Κατηγορία", EXPENSE_CATEGORIES, key="exp_cat")
                amount = st.number_input("Ποσό (€)", min_value=0.0, step=10.0, key="exp_amount")
                col_qty, col_unit = st.columns(2)
                quantity = col_qty.number_input("Ποσότητα", min_value=0.0, step=1.0, key="exp_qty")
                unit = col_unit.text_input("Μονάδα μέτρου (π.χ. τεμ, m3, kg)", key="exp_unit")
                expense_date = st.date_input("Ημερομηνία", value=datetime.date.today(), key="exp_date")
                description = st.text_input("Περιγραφή", key="exp_desc")
                if st.form_submit_button("Προσθήκη"):
                    add_expense(
                        project_id, amount, expense_date.isoformat(), category, description or None,
                        quantity or None, unit or None
                    )
                    st.rerun()

        expenses_data = list_expenses()
        st.write("Έξοδα:")
        st.table([
            {
                "Έργο": project_names.get(e[1], "-"),
                "Κατηγορία": e[2],
                "Ποσό": f"{e[3]:.2f} €",
                "Ποσότητα": f"{e[6]:g} {e[7]}" if e[6] and e[7] else (e[6] or "-"),
                "Ημερομηνία": e[4],
                "Περιγραφή": e[5],
            }
            for e in expenses_data
        ])

        st.write("Επεξεργασία / Διαγραφή εξόδου:")
        selected = select_row(
            expenses_data, lambda e: f"{e[4]} - {project_names.get(e[1], '-')} - {e[3]:.2f}€",
            key="edit_expense_select"
        )
        if selected is None:
            st.info("Δεν υπάρχουν έξοδα ακόμα.")
        elif not projects_data:
            st.warning("Πρόσθεσε πρώτα ένα έργο.")
        else:
            with st.form("edit_expense_form"):
                project_ids = list(project_options.keys())
                project_id = st.selectbox(
                    "Έργο", options=project_ids, format_func=lambda x: project_options[x],
                    index=project_ids.index(selected[1]) if selected[1] in project_ids else 0,
                    key="edit_exp_project"
                )
                category_index = EXPENSE_CATEGORIES.index(selected[2]) if selected[2] in EXPENSE_CATEGORIES else 0
                category = st.selectbox("Κατηγορία", EXPENSE_CATEGORIES, index=category_index, key="edit_exp_cat")
                amount = st.number_input(
                    "Ποσό (€)", min_value=0.0, value=selected[3], step=10.0, key="edit_exp_amount"
                )
                col_qty, col_unit = st.columns(2)
                quantity = col_qty.number_input(
                    "Ποσότητα", min_value=0.0, value=selected[6] or 0.0, step=1.0, key="edit_exp_qty"
                )
                unit = col_unit.text_input("Μονάδα μέτρου", value=selected[7] or "", key="edit_exp_unit")
                expense_date = st.date_input(
                    "Ημερομηνία", value=datetime.date.fromisoformat(selected[4]), key="edit_exp_date"
                )
                description = st.text_input("Περιγραφή", value=selected[5] or "", key="edit_exp_desc")
                col_a, col_b = st.columns(2)
                update_clicked = col_a.form_submit_button("Ενημέρωση")
                delete_clicked = col_b.form_submit_button("Διαγραφή")
                if update_clicked:
                    update_expense(
                        selected[0], project_id, amount, expense_date.isoformat(),
                        category, description or None, quantity or None, unit or None
                    )
                    st.rerun()
                if delete_clicked:
                    delete_expense(selected[0])
                    st.rerun()

    with col2:
        st.subheader("Νέο έσοδο")
        if not projects_data:
            st.warning("Πρόσθεσε πρώτα ένα έργο.")
        else:
            with st.form("add_income_form", clear_on_submit=True):
                project_id = st.selectbox(
                    "Έργο", options=list(project_options.keys()),
                    format_func=lambda x: project_options[x], key="inc_project"
                )
                amount = st.number_input("Ποσό (€)", min_value=0.0, step=10.0, key="inc_amount")
                vat_rate = st.selectbox(
                    "Συντελεστής ΦΠΑ", [24.0, 13.0, 6.0, 0.0],
                    format_func=lambda x: f"{x:.0f}%", key="inc_vat"
                )
                income_date = st.date_input("Ημερομηνία", value=datetime.date.today(), key="inc_date")
                description = st.text_input("Περιγραφή", key="inc_desc")
                if st.form_submit_button("Προσθήκη"):
                    # Ο πελάτης προκύπτει αυτόματα από το έργο που διάλεξες.
                    client_id = project_client_map.get(project_id)
                    add_income(project_id, amount, income_date.isoformat(), client_id, description or None, vat_rate)
                    st.rerun()

        income_data = list_income()
        st.write("Έσοδα:")
        st.table([
            {
                "Έργο": project_names.get(i[1], "-"),
                "Ποσό": f"{i[3]:.2f} €",
                "Ημερομηνία": i[4],
                "Περιγραφή": i[5],
                "ΦΠΑ": f"{i[6]:.0f}%" if i[6] is not None else "-",
                "ΦΠΑ για άκρη": f"{(i[3] * i[6] / 100):.2f} €" if i[6] else "-",
            }
            for i in income_data
        ])

        st.write("Επεξεργασία / Διαγραφή εσόδου:")
        selected = select_row(
            income_data, lambda i: f"{i[4]} - {project_names.get(i[1], '-')} - {i[3]:.2f}€",
            key="edit_income_select"
        )
        if selected is None:
            st.info("Δεν υπάρχουν έσοδα ακόμα.")
        elif not projects_data:
            st.warning("Πρόσθεσε πρώτα ένα έργο.")
        else:
            with st.form("edit_income_form"):
                project_ids = list(project_options.keys())
                project_id = st.selectbox(
                    "Έργο", options=project_ids, format_func=lambda x: project_options[x],
                    index=project_ids.index(selected[1]) if selected[1] in project_ids else 0,
                    key="edit_inc_project"
                )
                amount = st.number_input(
                    "Ποσό (€)", min_value=0.0, value=selected[3], step=10.0, key="edit_inc_amount"
                )
                vat_options = [24.0, 13.0, 6.0, 0.0]
                current_vat = selected[6] if selected[6] is not None else 24.0
                vat_rate = st.selectbox(
                    "Συντελεστής ΦΠΑ", vat_options,
                    index=vat_options.index(current_vat) if current_vat in vat_options else 0,
                    format_func=lambda x: f"{x:.0f}%", key="edit_inc_vat"
                )
                income_date = st.date_input(
                    "Ημερομηνία", value=datetime.date.fromisoformat(selected[4]), key="edit_inc_date"
                )
                description = st.text_input("Περιγραφή", value=selected[5] or "", key="edit_inc_desc")
                col_a, col_b = st.columns(2)
                update_clicked = col_a.form_submit_button("Ενημέρωση")
                delete_clicked = col_b.form_submit_button("Διαγραφή")
                if update_clicked:
                    # Ο πελάτης προκύπτει αυτόματα από το (τυχόν νέο) έργο.
                    client_id = project_client_map.get(project_id)
                    update_income(
                        selected[0], project_id, amount, income_date.isoformat(),
                        client_id, description or None, vat_rate
                    )
                    st.rerun()
                if delete_clicked:
                    delete_income(selected[0])
                    st.rerun()

# ------------------------------------------------------------- Φορολογίες
with tab_taxes:
    st.subheader("ΦΠΑ προς φύλαξη")
    st.metric("Σύνολο ΦΠΑ από όλα τα έσοδα", f"{get_total_vat_reserve():.2f} €")
    st.caption(
        "Υπολογίζεται από τον συντελεστή ΦΠΑ που όρισες σε κάθε έσοδο (tab Έξοδα & Έσοδα). "
        "Ο συνήθης συντελεστής είναι 24%, αλλά επισκευές/ανακαινίσεις κατοικιών έχουν 13% — "
        "επιβεβαίωσέ το με τον λογιστή σου, δεν είναι φορολογική συμβουλή."
    )

    st.subheader("Νέα φορολογική υποχρέωση")
    with st.form("add_tax_form", clear_on_submit=True):
        tax_type = st.text_input("Τύπος (π.χ. ΦΠΑ)")
        amount = st.number_input("Ποσό (€)", min_value=0.0, step=10.0, key="tax_amount")
        due_date = st.date_input("Προθεσμία", value=datetime.date.today())
        paid = st.checkbox("Πληρωμένο")
        if st.form_submit_button("Προσθήκη"):
            if tax_type:
                add_tax(tax_type, amount, due_date.isoformat(), 1 if paid else 0)
                st.rerun()
            else:
                st.error("Ο τύπος είναι υποχρεωτικός")

    taxes_data = list_taxes()
    st.subheader("Φορολογίες")
    st.table([
        {
            "Τύπος": t[1],
            "Ποσό": f"{t[2]:.2f} €",
            "Προθεσμία": t[3],
            "Πληρωμένο": "Ναι" if t[4] else "Όχι",
        }
        for t in taxes_data
    ])

    st.subheader("Επεξεργασία / Διαγραφή φορολογικής υποχρέωσης")
    selected = select_row(taxes_data, lambda t: f"{t[1]} - {t[3]}", key="edit_tax_select")
    if selected is None:
        st.info("Δεν υπάρχουν φορολογικές υποχρεώσεις ακόμα.")
    else:
        with st.form("edit_tax_form"):
            tax_type = st.text_input("Τύπος (π.χ. ΦΠΑ)", value=selected[1])
            amount = st.number_input("Ποσό (€)", min_value=0.0, value=selected[2], step=10.0)
            due_date = st.date_input("Προθεσμία", value=datetime.date.fromisoformat(selected[3]))
            paid = st.checkbox("Πληρωμένο", value=bool(selected[4]))
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                if tax_type:
                    update_tax(selected[0], tax_type, amount, due_date.isoformat(), 1 if paid else 0)
                    st.rerun()
                else:
                    st.error("Ο τύπος είναι υποχρεωτικός")
            if delete_clicked:
                delete_tax(selected[0])
                st.rerun()

    st.divider()
    st.subheader("Τιμολόγια")
    st.metric("Ανείσπρακτα τιμολόγια", f"{get_total_unpaid():.2f} €")

    projects_data = list_projects()
    project_names_inv = {p[0]: p[1] for p in projects_data}
    if not projects_data:
        st.warning("Πρόσθεσε πρώτα ένα έργο.")
    else:
        project_options_inv = {p[0]: p[1] for p in projects_data}
        with st.form("add_invoice_form", clear_on_submit=True):
            invoice_number = st.text_input("Αριθμός τιμολογίου")
            project_id = st.selectbox(
                "Έργο", options=list(project_options_inv.keys()),
                format_func=lambda x: project_options_inv[x], key="inv_project"
            )
            amount = st.number_input("Ποσό (€)", min_value=0.0, step=10.0, key="inv_amount")
            vat_rate = st.selectbox(
                "Συντελεστής ΦΠΑ", [24.0, 13.0, 6.0, 0.0],
                format_func=lambda x: f"{x:.0f}%", key="inv_vat"
            )
            invoice_date = st.date_input("Ημερομηνία", value=datetime.date.today(), key="inv_date")
            paid = st.checkbox("Έχει πληρωθεί", key="inv_paid")
            notes = st.text_input("Σημειώσεις", key="inv_notes")
            if st.form_submit_button("Προσθήκη"):
                add_invoice(
                    invoice_number or None, project_id, amount, invoice_date.isoformat(),
                    vat_rate, 1 if paid else 0, notes or None
                )
                st.rerun()

    invoices_data = list_invoices()
    st.write("Όλα τα τιμολόγια:")
    st.table([
        {
            "Αριθμός": inv[1] or "-",
            "Έργο": project_names_inv.get(inv[2], "-"),
            "Ποσό": f"{inv[3]:.2f} €",
            "ΦΠΑ": f"{inv[4]:.0f}%" if inv[4] is not None else "-",
            "Ημερομηνία": inv[5],
            "Πληρωμένο": "Ναι" if inv[6] else "Όχι",
            "Σημειώσεις": inv[7] or "-",
        }
        for inv in invoices_data
    ])

    st.write("Επεξεργασία / Διαγραφή τιμολογίου:")
    selected = select_row(
        invoices_data, lambda inv: f"{inv[1] or '(χωρίς αριθμό)'} - {project_names_inv.get(inv[2], '-')}",
        key="edit_invoice_select"
    )
    if selected is None:
        st.info("Δεν υπάρχουν τιμολόγια ακόμα.")
    elif not projects_data:
        st.warning("Πρόσθεσε πρώτα ένα έργο.")
    else:
        with st.form("edit_invoice_form"):
            invoice_number = st.text_input("Αριθμός τιμολογίου", value=selected[1] or "", key="edit_inv_number")
            project_ids_inv = list(project_options_inv.keys())
            project_id = st.selectbox(
                "Έργο", options=project_ids_inv, format_func=lambda x: project_options_inv[x],
                index=project_ids_inv.index(selected[2]) if selected[2] in project_ids_inv else 0,
                key="edit_inv_project"
            )
            amount = st.number_input(
                "Ποσό (€)", min_value=0.0, value=selected[3], step=10.0, key="edit_inv_amount"
            )
            vat_options_inv = [24.0, 13.0, 6.0, 0.0]
            current_vat_inv = selected[4] if selected[4] is not None else 24.0
            vat_rate = st.selectbox(
                "Συντελεστής ΦΠΑ", vat_options_inv,
                index=vat_options_inv.index(current_vat_inv) if current_vat_inv in vat_options_inv else 0,
                format_func=lambda x: f"{x:.0f}%", key="edit_inv_vat"
            )
            invoice_date = st.date_input(
                "Ημερομηνία", value=datetime.date.fromisoformat(selected[5]), key="edit_inv_date"
            )
            paid = st.checkbox("Έχει πληρωθεί", value=bool(selected[6]), key="edit_inv_paid")
            notes = st.text_input("Σημειώσεις", value=selected[7] or "", key="edit_inv_notes")
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                update_invoice(
                    selected[0], invoice_number or None, project_id, amount,
                    invoice_date.isoformat(), vat_rate, 1 if paid else 0, notes or None
                )
                st.rerun()
            if delete_clicked:
                delete_invoice(selected[0])
                st.rerun()

# ----------------------------------------------------------------- Καιρός
with tab_weather:
    city = st.text_input("Πόλη", value="Athens", key="weather_city")
    weather = get_current_weather(city)
    if weather is None:
        st.info(
            "Δεν βρέθηκε ο καιρός. Έλεγξε ότι έχεις βάλει σωστό API key "
            "στο weather.py και ότι η πόλη γράφεται σωστά (π.χ. 'Athens')."
        )
    else:
        emoji = get_weather_emoji(weather["main"])
        col_icon, col_info = st.columns([1, 3])
        with col_icon:
            st.markdown(
                f"<div style='font-size:88px; line-height:1; text-align:center'>{emoji}</div>",
                unsafe_allow_html=True
            )
        with col_info:
            st.markdown(f"#### {city}")
            st.markdown(f"## {weather['temperature']:.1f}°C")
            st.write(weather["description"].capitalize())
            st.caption(
                f"Αίσθηση σαν {weather['feels_like']:.1f}°C · "
                f"Υγρασία {weather['humidity']}% · "
                f"Άνεμος {weather['wind_speed']} m/s"
            )

        forecast = get_forecast(city)
        if forecast:
            st.write("")
            st.write("**Επόμενες μέρες**")
            cols = st.columns(len(forecast))
            for col, day in zip(cols, forecast):
                with col:
                    day_date = datetime.date.fromisoformat(day["date"])
                    day_emoji = get_weather_emoji(day["main"])
                    st.markdown(f"**{day_date.strftime('%a %d/%m')}**")
                    st.markdown(
                        f"<div style='font-size:40px; text-align:center'>{day_emoji}</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"{day['temp_min']:.0f}° / {day['temp_max']:.0f}°")

# -------------------------------------------------------------- Ημερολόγιο
with tab_calendar:
    MONTH_NAMES_CAL = [
        "Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος",
        "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"
    ]
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = datetime.date.today().year
    if "cal_month" not in st.session_state:
        st.session_state.cal_month = datetime.date.today().month

    col_prev, col_title, col_next = st.columns([1, 4, 1])
    if col_prev.button("◀ Προηγούμενος", key="cal_prev"):
        st.session_state.cal_month -= 1
        if st.session_state.cal_month < 1:
            st.session_state.cal_month = 12
            st.session_state.cal_year -= 1
        st.rerun()
    if col_next.button("Επόμενος ▶", key="cal_next"):
        st.session_state.cal_month += 1
        if st.session_state.cal_month > 12:
            st.session_state.cal_month = 1
            st.session_state.cal_year += 1
        st.rerun()
    col_title.markdown(
        f"<h3 style='text-align:center'>{MONTH_NAMES_CAL[st.session_state.cal_month - 1]} "
        f"{st.session_state.cal_year}</h3>",
        unsafe_allow_html=True
    )

    events_by_date = {}
    for e in list_events():
        events_by_date.setdefault(e[1], []).append(e[2])

    today_str = datetime.date.today().isoformat()
    weekday_names = ["Δευ", "Τρι", "Τετ", "Πεμ", "Παρ", "Σαβ", "Κυρ"]
    header_cols = st.columns(7)
    for col, wd in zip(header_cols, weekday_names):
        col.markdown(f"<div style='text-align:center'><b>{wd}</b></div>", unsafe_allow_html=True)

    if "cal_selected_date" not in st.session_state:
        st.session_state.cal_selected_date = today_str

    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(
        st.session_state.cal_year, st.session_state.cal_month
    )
    for week in weeks:
        row_cols = st.columns(7)
        for col, day in zip(row_cols, week):
            if day == 0:
                col.markdown("&nbsp;", unsafe_allow_html=True)
                continue
            date_str = f"{st.session_state.cal_year:04d}-{st.session_state.cal_month:02d}-{day:02d}"
            day_events = events_by_date.get(date_str, [])
            is_today = date_str == today_str
            is_selected = date_str == st.session_state.cal_selected_date
            day_label = f"📍{day}" if is_today else f"{day}"
            label = f"{day_label} •" if day_events else day_label
            button_type = "primary" if is_selected else "secondary"
            if col.button(label, key=f"cal_day_{date_str}", use_container_width=True, type=button_type):
                st.session_state.cal_selected_date = date_str
                st.rerun()

    st.divider()

    # ------------------------------------------------ Επιλεγμένη ημέρα
    selected_date = st.session_state.cal_selected_date
    st.subheader(f"📅 {selected_date}")
    day_events_full = [e for e in list_events() if e[1] == selected_date]
    if not day_events_full:
        st.caption("Καμία υπενθύμιση αυτή τη μέρα.")
    else:
        for e in day_events_full:
            st.write(f"- **{e[2]}** ({e[3] or '-'}){' - ' + e[4] if e[4] else ''}")

    with st.form("add_event_for_day", clear_on_submit=True):
        st.write(f"Νέα υπενθύμιση για {selected_date}")
        title = st.text_input("Τίτλος")
        event_type = st.selectbox("Τύπος", EVENT_TYPES, key="day_event_type")
        notes = st.text_area("Σημειώσεις", key="day_event_notes")
        if st.form_submit_button("Προσθήκη"):
            if title:
                add_event(selected_date, title, event_type, notes or None)
                st.rerun()
            else:
                st.error("Ο τίτλος είναι υποχρεωτικός")

    st.divider()
    st.subheader("Επερχόμενα")
    upcoming = get_upcoming_events()
    if not upcoming:
        st.info(f"Καμία υπενθύμιση τις επόμενες {7} μέρες.")
    else:
        icons = {"Πέρασε": "🔴", "Σήμερα": "🟠", "Σύντομα": "🟡"}
        for e in upcoming:
            status = e[-1]
            st.write(f"{icons.get(status, '⚪')} **{e[2]}** ({e[3] or '-'}) - {e[1]} - {status}")

    events_data = list_events()
    st.subheader("Όλες οι υπενθυμίσεις")
    st.table([
        {
            "Ημερομηνία": e[1],
            "Τίτλος": e[2],
            "Τύπος": e[3] or "-",
            "Σημειώσεις": e[4] or "-",
        }
        for e in events_data
    ])

    st.subheader("Επεξεργασία / Διαγραφή υπενθύμισης")
    selected = select_row(events_data, lambda e: f"{e[1]} - {e[2]}", key="edit_event_select")
    if selected is None:
        st.info("Δεν υπάρχουν υπενθυμίσεις ακόμα.")
    else:
        with st.form("edit_event_form"):
            event_date = st.date_input(
                "Ημερομηνία", value=datetime.date.fromisoformat(selected[1]), key="edit_event_date"
            )
            title = st.text_input("Τίτλος", value=selected[2], key="edit_event_title")
            type_index = EVENT_TYPES.index(selected[3]) if selected[3] in EVENT_TYPES else 0
            event_type = st.selectbox("Τύπος", EVENT_TYPES, index=type_index, key="edit_event_type")
            notes = st.text_area("Σημειώσεις", value=selected[4] or "", key="edit_event_notes")
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                if title:
                    update_event(selected[0], event_date.isoformat(), title, event_type, notes or None)
                    st.rerun()
                else:
                    st.error("Ο τίτλος είναι υποχρεωτικός")
            if delete_clicked:
                delete_event(selected[0])
                st.rerun()

# ------------------------------------------------------------- Οχήματα
with tab_vehicles:
    st.subheader("Νέο όχημα")
    with st.form("add_vehicle_form", clear_on_submit=True):
        name = st.text_input("Όνομα / Τύπος οχήματος")
        license_plate = st.text_input("Πινακίδα")
        insurance_expiry = st.date_input("Λήξη ασφάλειας", value=datetime.date.today())
        kteo_expiry = st.date_input("Λήξη ΚΤΕΟ", value=datetime.date.today(), key="vehicle_kteo")
        road_tax_expiry = st.date_input("Λήξη τελών κυκλοφορίας", value=datetime.date.today(), key="vehicle_road_tax")
        has_service = st.checkbox("Έχει γίνει σέρβις;")
        last_service_date = st.date_input("Ημερομηνία τελευταίου σέρβις", value=datetime.date.today(), key="vehicle_service_date")
        service_notes = st.text_area("Σημειώσεις σέρβις (τι έγινε)", key="vehicle_service_notes")
        notes = st.text_input("Γενικές σημειώσεις")
        if st.form_submit_button("Προσθήκη"):
            if name:
                add_vehicle(
                    name, license_plate or None, insurance_expiry.isoformat(),
                    kteo_expiry.isoformat(), road_tax_expiry.isoformat(),
                    last_service_date.isoformat() if has_service else None,
                    service_notes or None, notes or None
                )
                st.rerun()
            else:
                st.error("Το όνομα είναι υποχρεωτικό")

    st.subheader("Οχήματα")
    st.table([
        {
            "Όνομα": v[1],
            "Πινακίδα": v[2] or "-",
            "Ασφάλεια λήγει": v[3] or "-",
            "Κατάσταση ασφάλειας": v[9],
            "ΚΤΕΟ λήγει": v[4] or "-",
            "Κατάσταση ΚΤΕΟ": v[10],
            "Τέλη κυκλοφορίας λήγουν": v[5] or "-",
            "Κατάσταση τελών": v[11],
            "Τελευταίο σέρβις": v[6] or "-",
            "Σημειώσεις σέρβις": v[7] or "-",
            "Γενικές σημειώσεις": v[8] or "-",
        }
        for v in list_vehicles_with_status()
    ])

    st.subheader("Επεξεργασία / Διαγραφή οχήματος")
    vehicles_data = list_vehicles()
    selected = select_row(vehicles_data, lambda v: f"{v[1]} ({v[2] or '-'})", key="edit_vehicle_select")
    if selected is None:
        st.info("Δεν υπάρχουν οχήματα ακόμα.")
    else:
        with st.form("edit_vehicle_form"):
            name = st.text_input("Όνομα / Τύπος οχήματος", value=selected[1])
            license_plate = st.text_input("Πινακίδα", value=selected[2] or "")
            insurance_expiry = st.date_input(
                "Λήξη ασφάλειας",
                value=datetime.date.fromisoformat(selected[3]) if selected[3] else datetime.date.today()
            )
            kteo_expiry = st.date_input(
                "Λήξη ΚΤΕΟ",
                value=datetime.date.fromisoformat(selected[4]) if selected[4] else datetime.date.today(),
                key="edit_vehicle_kteo"
            )
            road_tax_expiry = st.date_input(
                "Λήξη τελών κυκλοφορίας",
                value=datetime.date.fromisoformat(selected[5]) if selected[5] else datetime.date.today(),
                key="edit_vehicle_road_tax"
            )
            has_service = st.checkbox("Έχει γίνει σέρβις;", value=bool(selected[6]))
            last_service_date = st.date_input(
                "Ημερομηνία τελευταίου σέρβις",
                value=datetime.date.fromisoformat(selected[6]) if selected[6] else datetime.date.today(),
                key="edit_vehicle_service_date"
            )
            service_notes = st.text_area("Σημειώσεις σέρβις (τι έγινε)", value=selected[7] or "", key="edit_vehicle_service_notes")
            notes = st.text_input("Γενικές σημειώσεις", value=selected[8] or "")
            col_a, col_b = st.columns(2)
            update_clicked = col_a.form_submit_button("Ενημέρωση")
            delete_clicked = col_b.form_submit_button("Διαγραφή")
            if update_clicked:
                if name:
                    update_vehicle(
                        selected[0], name, license_plate or None, insurance_expiry.isoformat(),
                        kteo_expiry.isoformat(), road_tax_expiry.isoformat(),
                        last_service_date.isoformat() if has_service else None,
                        service_notes or None, notes or None
                    )
                    st.rerun()
                else:
                    st.error("Το όνομα είναι υποχρεωτικό")
            if delete_clicked:
                delete_vehicle(selected[0])
                st.rerun()

# ---------------------------------------------------------------- Αναφορές
with tab_reports:
    MONTH_NAMES = [
        "Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος",
        "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"
    ]
    current_year = datetime.date.today().year
    years = list(range(current_year - 3, current_year + 1))

    st.subheader("Μηνιαία αναφορά")
    col_y, col_m = st.columns(2)
    report_year = col_y.selectbox("Έτος", years, index=len(years) - 1, key="report_year")
    report_month = col_m.selectbox(
        "Μήνας", list(range(1, 13)), index=datetime.date.today().month - 1,
        format_func=lambda m: MONTH_NAMES[m - 1], key="report_month"
    )

    monthly = get_monthly_report(report_year, report_month)
    col1, col2, col3 = st.columns(3)
    col1.metric("Τζίρος", f"{monthly['turnover']:.2f} €")
    col2.metric("Έξοδα", f"{monthly['expenses_total']:.2f} €")
    col3.metric("Ημερομίσθια", f"{monthly['wages_total']:.2f} €")
    col4, col5, col6 = st.columns(3)
    col4.metric("ΦΠΑ προς απόδοση", f"{monthly['vat_due']:.2f} €")
    col5.metric("Λοιπές φορολογίες", f"{monthly['other_taxes']:.2f} €")
    col6.metric(
        "Καθαρά κέρδη", f"{monthly['net_profit']:.2f} €",
        f"{monthly['profit_margin_pct']:.1f}% περιθώριο"
    )

    st.divider()

    st.subheader(f"Ετήσια αναφορά {report_year}")
    yearly_totals, monthly_breakdown = get_yearly_report(report_year)
    col1, col2, col3 = st.columns(3)
    col1.metric("Τζίρος έτους", f"{yearly_totals['turnover']:.2f} €")
    col2.metric(
        "Σύνολο εξόδων + ημερομισθίων",
        f"{(yearly_totals['expenses_total'] + yearly_totals['wages_total']):.2f} €"
    )
    col3.metric(
        "Καθαρά κέρδη έτους", f"{yearly_totals['net_profit']:.2f} €",
        f"{yearly_totals['profit_margin_pct']:.1f}% περιθώριο"
    )

    st.write("Ανά μήνα:")
    st.table([
        {
            "Μήνας": MONTH_NAMES[m["month"] - 1],
            "Τζίρος": f"{m['turnover']:.2f} €",
            "Έξοδα": f"{m['expenses_total']:.2f} €",
            "Ημερομίσθια": f"{m['wages_total']:.2f} €",
            "ΦΠΑ": f"{m['vat_due']:.2f} €",
            "Καθαρά κέρδη": f"{m['net_profit']:.2f} €",
            "Περιθώριο": f"{m['profit_margin_pct']:.1f}%",
        }
        for m in monthly_breakdown
    ])

    st.subheader(f"Κατανομή εξόδων ανά κατηγορία ({report_year})")
    breakdown = get_expense_breakdown_by_category(report_year)
    if not breakdown:
        st.info("Δεν υπάρχουν έξοδα καταχωρημένα για αυτό το έτος.")
    else:
        st.table([
            {"Κατηγορία": category, "Ποσό": f"{amount:.2f} €", "Ποσοστό": f"{pct:.1f}%"}
            for category, amount, pct in breakdown
        ])
