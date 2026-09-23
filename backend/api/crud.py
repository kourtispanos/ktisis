from fastapi import APIRouter, Depends, HTTPException

from backend.api.deps import require_auth
from backend.database.db import get_connection


def column_names(table):
    # Τα ονόματα των στηλών διαβάζονται από την ίδια τη βάση, ώστε να
    # δουλεύει σωστά ακόμα και σε παλιότερες βάσεις (ALTER TABLE).
    conn = get_connection()
    names = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
    conn.close()
    return names


def rows_to_dicts(table, rows, extra_columns=()):
    columns = column_names(table) + list(extra_columns)
    return [dict(zip(columns, row)) for row in rows]


def make_crud_router(prefix, table, schema, list_fn, add_fn, update_fn, delete_fn, extra_columns=(), enrich=None):
    router = APIRouter(prefix=prefix, dependencies=[Depends(require_auth)])

    @router.get("")
    def list_all():
        items = rows_to_dicts(table, list_fn(), extra_columns)
        if enrich:
            for item in items:
                enrich(item)
        return items

    @router.post("", status_code=201)
    def create(item: schema):
        add_fn(**item.model_dump())
        return {"ok": True}

    @router.put("/{item_id}")
    def update(item_id: int, item: schema):
        update_fn(item_id, **item.model_dump())
        return {"ok": True}

    @router.delete("/{item_id}")
    def delete(item_id: int):
        # Οι συναρτήσεις με FOREIGN KEY επιστρέφουν False αν η εγγραφή χρησιμοποιείται αλλού
        if delete_fn(item_id) is False:
            raise HTTPException(
                status_code=409,
                detail="Δεν μπορεί να διαγραφεί: χρησιμοποιείται σε άλλες εγγραφές",
            )
        return {"ok": True}

    return router
