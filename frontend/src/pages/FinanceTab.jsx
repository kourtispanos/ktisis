import { api } from "../api.js";
import { CrudSection, Loading } from "../components/ui.jsx";
import { dash, money, nameMap, percent, today, toOptions, useLoad, VAT_OPTIONS } from "../lib.js";

export default function FinanceTab({ meta }) {
  const { data, error, reload } = useLoad(() => Promise.all([
    api.get("/projects"), api.get("/expenses"), api.get("/income"),
  ]));
  if (!data) return <Loading error={error} />;

  const [projects, expenses, income] = data;
  const projectNames = nameMap(projects);
  const clientByProject = Object.fromEntries(projects.map((p) => [p.id, p.client_id]));
  const blocker = projects.length ? null : "Πρόσθεσε πρώτα ένα έργο.";
  const projectField = {
    name: "project_id", label: "Έργο", type: "select", required: true,
    options: toOptions(projects, (p) => p.name),
  };

  const expenseFields = [
    projectField,
    { name: "category", label: "Κατηγορία", type: "select", options: meta.expense_categories.map((c) => ({ value: c, label: c })) },
    { name: "amount", label: "Ποσό (€)", type: "number", required: true, min: 0, step: 10 },
    { name: "quantity", label: "Ποσότητα", type: "number", min: 0, step: 1 },
    { name: "unit", label: "Μονάδα μέτρου (π.χ. τεμ, m3, kg)" },
    { name: "expense_date", label: "Ημερομηνία", type: "date", required: true, default: today },
    { name: "description", label: "Περιγραφή", wide: true },
  ];

  const incomeFields = [
    projectField,
    { name: "amount", label: "Ποσό (€)", type: "number", required: true, min: 0, step: 10 },
    { name: "vat_rate", label: "Συντελεστής ΦΠΑ", type: "select", options: VAT_OPTIONS, default: meta.default_vat_rate },
    { name: "income_date", label: "Ημερομηνία", type: "date", required: true, default: today },
    { name: "description", label: "Περιγραφή", wide: true },
  ];

  return (
    <div className="columns">
      <CrudSection
        title="Νέο έξοδο"
        listTitle="Έξοδα"
        path="/expenses"
        blocker={blocker}
        fields={expenseFields}
        rows={expenses}
        onChange={reload}
        columns={[
          { label: "Έργο", render: (e) => projectNames[e.project_id] ?? "-" },
          { label: "Κατηγορία", render: (e) => dash(e.category) },
          { label: "Ποσό", num: true, render: (e) => money(e.amount) },
          { label: "Ποσότητα", num: true, render: (e) => (e.quantity ? `${e.quantity}${e.unit ? " " + e.unit : ""}` : "-") },
          { label: "Ημερομηνία", render: (e) => e.expense_date },
          { label: "Περιγραφή", render: (e) => dash(e.description) },
        ]}
      />

      <CrudSection
        title="Νέο έσοδο"
        listTitle="Έσοδα"
        path="/income"
        blocker={blocker}
        fields={incomeFields}
        rows={income}
        onChange={reload}
        // Ο πελάτης προκύπτει αυτόματα από το έργο που διάλεξες
        toPayload={(values) => ({ ...values, client_id: clientByProject[values.project_id] ?? null })}
        columns={[
          { label: "Έργο", render: (i) => projectNames[i.project_id] ?? "-" },
          { label: "Ποσό", num: true, render: (i) => money(i.amount) },
          { label: "Ημερομηνία", render: (i) => i.income_date },
          { label: "Περιγραφή", render: (i) => dash(i.description) },
          { label: "ΦΠΑ", num: true, render: (i) => percent(i.vat_rate) },
          { label: "ΦΠΑ για άκρη", num: true, render: (i) => (i.vat_rate ? money((i.amount * i.vat_rate) / 100) : "-") },
        ]}
      />
    </div>
  );
}
