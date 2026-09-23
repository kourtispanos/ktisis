import { useCallback, useEffect, useState } from "react";

// ---------- Μορφοποίηση ----------

export const money = (value) => (value == null ? "-" : `${Number(value).toFixed(2)} €`);

const pad = (n) => String(n).padStart(2, "0");

// Τοπική ημερομηνία (όχι UTC), ώστε το βράδυ να μην εμφανίζεται η επόμενη μέρα
export function today() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export const dash = (value) => (value == null || value === "" ? "-" : value);

export const yesNo = (value) => (value ? "Ναι" : "Όχι");

export const percent = (value) => (value == null ? "-" : `${Number(value).toFixed(0)}%`);

export const MONTH_NAMES = [
  "Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος",
  "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος",
];

export const VAT_OPTIONS = [24, 13, 6, 0].map((rate) => ({ value: rate, label: `${rate}%` }));

export const toOptions = (rows, label) => rows.map((row) => ({ value: row.id, label: label(row) }));

export const nameMap = (rows) => Object.fromEntries(rows.map((row) => [row.id, row.name]));


// ---------- Φόρτωση δεδομένων ----------

// Φορτώνει δεδομένα από το API και επιστρέφει reload() για ανανέωση μετά από αλλαγές.
export function useLoad(loader, deps = []) {
  const [state, setState] = useState({ data: null, error: null });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cancelled = false;
    loader().then(
      (data) => !cancelled && setState({ data, error: null }),
      (error) => !cancelled && setState({ data: null, error: error.message }),
    );
    return () => { cancelled = true; };
  }, [...deps, version]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  return { ...state, reload };
}
