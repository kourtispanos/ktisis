import mimetypes
import os
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import api
from backend.database.create_db import create_tables

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# Στα Windows το registry μπορεί να δώσει λάθος τύπο στα .js και ο browser να μην τα εκτελεί
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

app = FastAPI(title="Ktisis")


@app.on_event("startup")
def startup():
    # Ασφαλές σε υπάρχουσα βάση (CREATE TABLE IF NOT EXISTS) - προσθέτει τυχόν νέους πίνακες
    create_tables()


app.include_router(api)

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
