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

    db_path = os.path.join(app_dir, "ktisis.db")
    if not os.path.exists(db_path):
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
