import os
import sys
import threading
import time
import traceback
import webbrowser


def main():
    if getattr(sys, "frozen", False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    sys.path.insert(0, app_dir)
    sys.path.insert(0, os.path.join(app_dir, "database"))

    # Τρέχει πάντα, όχι μόνο όταν λείπει η βάση - CREATE TABLE IF NOT EXISTS
    # είναι ασφαλές σε υπάρχουσα βάση, και έτσι προστίθενται αυτόματα νέοι
    # πίνακες από ενημερώσεις (π.χ. το 'users') σε παλιότερες εγκαταστάσεις.
    from create_db import create_tables
    create_tables()

    from streamlit.web import cli as stcli

    app_path = os.path.join(app_dir, "app.py")

    def open_browser_later():
        time.sleep(3)
        webbrowser.open("http://localhost:8501")

    threading.Thread(target=open_browser_later, daemon=True).start()

    sys.argv = [
        "streamlit", "run", app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n\nΚάτι πήγε στραβά κατά την εκκίνηση:\n")
        traceback.print_exc()
        input("\nΠάτησε Enter για να κλείσεις...")
