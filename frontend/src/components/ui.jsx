import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import { Form, useToast } from "./forms.jsx";

// Μικρά κοινά κομμάτια εμφάνισης

export function Card({ title, children }) {
  return (
    <section className="card">
      {title && <h3>{title}</h3>}
      {children}
    </section>
  );
}

export function Notice({ kind = "", children }) {
  return <div className={`notice ${kind}`}>{children}</div>;
}

export function Metric({ label, value, sub, className = "" }) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className={`value ${className}`}>{value}</div>
      {sub && <div className="sub">{sub}</div>}
    </div>
  );
}

const BADGE_KIND = { OK: "ok", "Λήγει σύντομα": "warn", "Έληξε": "bad" };

export function Badge({ text }) {
  return <span className={`badge ${BADGE_KIND[text] || ""}`}>{text}</span>;
}

export function DataTable({ columns, rows, actions }) {
  if (!rows.length) return <div className="empty">Δεν υπάρχουν εγγραφές ακόμα.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c) => <th key={c.label} className={c.num ? "num" : ""}>{c.label}</th>)}
            {actions && <th />}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map((c) => <td key={c.label} className={c.num ? "num" : ""}>{c.render(row)}</td>)}
              {actions && <td className="actions">{actions(row)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Loading({ error }) {
  if (error) return <Notice kind="error">{error}</Notice>;
  return <Notice>Φόρτωση...</Notice>;
}


// Παράθυρο διαλόγου που ανοίγει μόλις εμφανιστεί και κλείνει με Esc ή με το onClose
export function Dialog({ title = "Επεξεργασία", onClose, children }) {
  const ref = useRef(null);
  useEffect(() => {
    const dialog = ref.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);
  return (
    <dialog ref={ref} onClose={onClose}>
      <h3>{title}</h3>
      {children}
    </dialog>
  );
}

// Φόρμα προσθήκης + πίνακας με κουμπιά επεξεργασίας/διαγραφής.
// Η επεξεργασία ανοίγει σε παράθυρο διαλόγου με την ίδια φόρμα, προσυμπληρωμένη.
export function CrudSection({
  title, listTitle, path, fields, columns, rows, onChange,
  toPayload = (values) => values, blocker, initial, beforeList,
}) {
  const toast = useToast();
  const [editing, setEditing] = useState(null);
  const [formKey, setFormKey] = useState(0);

  const add = async (values) => {
    await api.post(path, toPayload(values, null));
    toast("Η εγγραφή προστέθηκε");
    setFormKey((k) => k + 1);
    onChange();
  };

  const update = async (values) => {
    await api.put(`${path}/${editing.id}`, toPayload(values, editing));
    toast("Η εγγραφή ενημερώθηκε");
    setEditing(null);
    onChange();
  };

  const remove = async (row) => {
    if (!confirm("Να διαγραφεί η εγγραφή;")) return;
    try {
      await api.delete(`${path}/${row.id}`);
      toast("Η εγγραφή διαγράφηκε");
      onChange();
    } catch (error) {
      toast(error.message, "error");
    }
  };

  return (
    <div>
      <Card title={title}>
        {blocker
          ? <Notice kind="warn">{blocker}</Notice>
          : <Form key={formKey} fields={fields} initial={initial} submitLabel="Προσθήκη" onSubmit={add} />}
      </Card>

      <Card title={listTitle}>
        {beforeList}
        <DataTable
          columns={columns}
          rows={rows}
          actions={(row) => (
            <>
              <button className="small" onClick={() => setEditing(row)}>Επεξεργασία</button>
              <button className="small danger" onClick={() => remove(row)}>Διαγραφή</button>
            </>
          )}
        />
      </Card>

      {editing && (
        <Dialog onClose={() => setEditing(null)}>
          <Form fields={fields} initial={editing} submitLabel="Ενημέρωση" onSubmit={update}>
            <button type="button" onClick={() => setEditing(null)}>Άκυρο</button>
          </Form>
        </Dialog>
      )}
    </div>
  );
}
