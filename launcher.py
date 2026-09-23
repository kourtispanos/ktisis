import os
import socket
import sys
import threading
import time
import traceback
import webbrowser

import uvicorn

HOST = "127.0.0.1"  # μόνο αυτός ο υπολογιστής - δεν είναι προσβάσιμο από το δίκτυο
PREFERRED_PORT = 8000


def find_free_port(preferred):
    """Επιστρέφει την προτιμώμενη πόρτα, ή μια τυχαία ελεύθερη αν είναι πιασμένη."""
    for port in (preferred, 0):
        with socket.socket() as probe:
            try:
                probe.bind((HOST, port))
            except OSError:
                continue
            return probe.getsockname()[1]


def open_browser_when_ready(port, timeout=10):
    """Περιμένει να απαντήσει ο server και μετά ανοίγει τον browser."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex((HOST, port)) == 0:
                webbrowser.open(f"http://{HOST}:{port}")
                return
        time.sleep(0.1)


def main():
    if getattr(sys, "frozen", False):
        # Στο εγκατεστημένο exe, το local_settings.py (API key καιρού) μένει δίπλα του
        sys.path.insert(0, os.path.dirname(sys.executable))

    from backend.main import app

    port = find_free_port(PREFERRED_PORT)
    threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True).start()

    print(f"Το Ktisis τρέχει στο http://{HOST}:{port}")
    print("Κλείσε αυτό το παράθυρο για να σταματήσει η εφαρμογή.\n")
    uvicorn.run(app, host=HOST, port=port, log_level="warning")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n\nΚάτι πήγε στραβά κατά την εκκίνηση:\n")
        traceback.print_exc()
        input("\nΠάτησε Enter για να κλείσεις...")
