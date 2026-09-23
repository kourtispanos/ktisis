import { api } from "../api.js";
import { Card, CrudSection, Loading, Metric } from "../components/ui.jsx";
import { dash, money, nameMap, percent, today, toOptions, useLoad, VAT_OPTIONS, yesNo } from "../lib.js";

const TAX_FIELDS = [
  { name: "tax_type", label: "Τύπος (π.χ. ΦΠΑ)", required: true },
  { name: "amount", label: "Ποσό (€)", type: "number", required: true, min: 0, step: 10 },
  { name: "due_date", label: "Προθεσμία", type: "date", required: true, default: today },
  { name: "paid", label: "Πληρωμένο", type: "checkbox" },
];

const paidToInt = (values) => ({ ...values, paid: values.paid ? 1 : 0 });

export default function TaxesTab({ meta }) {
  const { data, error, reload } = useLoad(() => Promise.all([
    api.get("/income/vat-reserve"), api.get("/invoices/unpaid-total"),
    api.get("/taxes"), api.get("/invoices"), api.get("/projects"),
  ]));
  if (!data) return <Loading error={error} />;

  const [vat, unpaid, taxes, invoices, projects] = data;
  const projectNames = nameMap(projects);

  const invoiceFields = [
    { name: "invoice_number", label: "Αριθμός τιμολογίου" },
    { name: "project_id", label: "Έργο", type: "select", required: true, options: toOptions(projects, (p) => p.name) },
    { name: "amount", label: "Ποσό (€)", type: "number", required: true, min: 0, step: 10 },
    { name: "vat_rate", label: "Συντελεστής ΦΠΑ", type: "select", options: VAT_OPTIONS, default: meta.default_vat_rate },
    { name: "invoice_date", label: "Ημερομηνία", type: "date", required: true, default: today },
    { name: "paid", label: "Έχει πληρωθεί", type: "checkbox" },
    { name: "notes", label: "Σημειώσεις", wide: true },
  ];

  return (
    <>
      <Card title="ΦΠΑ προς φύλαξη">
        <div className="metrics">
          <Metric label="Σύνολο ΦΠΑ από όλα τα έσοδα" value={money(vat.total)} />
        </div>
        <p className="caption">
          Υπολογίζεται από τον συντελεστή ΦΠΑ που όρισες σε κάθε έσοδο (tab Έξοδα & Έσοδα).
          Ο συνήθης συντελεστής είναι 24%, αλλά επισκευές/ανακαινίσεις κατοικιών έχουν 13% —
          επιβεβαίωσέ το με τον λογιστή σου, δεν είναι φορολογική συμβουλή.
        </p>
      </Card>

      <CrudSection
        title="Νέα φορολογική υποχρέωση"
        listTitle="Φορολογίες"
        path="/taxes"
        fields={TAX_FIELDS}
        rows={taxes}
        onChange={reload}
        toPayload={paidToInt}
        columns={[
          { label: "Τύπος", render: (t) => t.tax_type },
          { label: "Ποσό", num: true, render: (t) => money(t.amount) },
          { label: "Προθεσμία", render: (t) => t.due_date },
          { label: "Πληρωμένο", render: (t) => yesNo(t.paid) },
        ]}
      />

      <h2>Τιμολόγια</h2>
      <div className="metrics">
        <Metric label="Ανείσπρακτα τιμολόγια" value={money(unpaid.total)} />
      </div>

      <CrudSection
        title="Νέο τιμολόγιο"
        listTitle="Όλα τα τιμολόγια"
        path="/invoices"
        blocker={projects.length ? null : "Πρόσθεσε πρώτα ένα έργο."}
        fields={invoiceFields}
        rows={invoices}
        onChange={reload}
        toPayload={paidToInt}
        columns={[
          { label: "Αριθμός", render: (i) => dash(i.invoice_number) },
          { label: "Έργο", render: (i) => projectNames[i.project_id] ?? "-" },
          { label: "Ποσό", num: true, render: (i) => money(i.amount) },
          { label: "ΦΠΑ", num: true, render: (i) => percent(i.vat_rate) },
          { label: "Ημερομηνία", render: (i) => i.invoice_date },
          { label: "Πληρωμένο", render: (i) => yesNo(i.paid) },
          { label: "Σημειώσεις", render: (i) => dash(i.notes) },
        ]}
      />
    </>
  );
}
