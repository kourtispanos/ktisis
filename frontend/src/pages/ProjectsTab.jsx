import { api } from "../api.js";
import { Card, CrudSection, Loading, Notice } from "../components/ui.jsx";
import { dash, money, nameMap, today, toOptions, useLoad } from "../lib.js";

const STATUSES = ["ενεργό", "σε παύση", "ολοκληρωμένο"].map((s) => ({ value: s, label: s }));

function BudgetItem({ pf }) {
  return (
    <div className="budget-item">
      <strong>{pf.name}</strong>
      {pf.budget ? (
        <>
          <div className="progress">
            <div className={pf.spent_pct > 100 ? "over" : ""} style={{ width: `${Math.min(pf.spent_pct, 100)}%` }} />
          </div>
          <div className="caption">
            {money(pf.spent)} / {money(pf.budget)} ({pf.spent_pct.toFixed(1)}%)
          </div>
          {pf.spent_pct > 100
            ? <Notice kind="error">⚠️ Υπέρβαση προϋπολογισμού κατά {money(-pf.remaining)}</Notice>
            : <div className="caption">Υπόλοιπο προϋπολογισμού: {money(pf.remaining)}</div>}
        </>
      ) : (
        <div className="caption">Δεν έχει οριστεί προϋπολογισμός για αυτό το έργο.</div>
      )}
      <div className="caption">
        Έξοδα: {money(pf.expenses)} · Ημερομίσθια: {money(pf.wages)} · Έσοδα εισπραχθέντα: {money(pf.income)}
      </div>
    </div>
  );
}

export default function ProjectsTab() {
  const { data, error, reload } = useLoad(() => Promise.all([
    api.get("/projects"), api.get("/clients"), api.get("/projects/financials/all"),
  ]));
  if (!data) return <Loading error={error} />;

  const [projects, clients, financials] = data;
  const clientNames = nameMap(clients);

  const fields = [
    { name: "name", label: "Όνομα έργου", required: true },
    { name: "client_id", label: "Πελάτης", type: "select", required: true, options: toOptions(clients, (c) => c.name) },
    { name: "location", label: "Τοποθεσία (πόλη)" },
    { name: "start_date", label: "Ημερομηνία έναρξης", type: "date", default: today },
    { name: "status", label: "Κατάσταση", type: "select", options: STATUSES },
    { name: "budget", label: "Προϋπολογισμός (€)", type: "number", min: 0, step: 100 },
    { name: "end_date", label: "Έχει ολοκληρωθεί με γνωστή ημερομηνία;", type: "optdate" },
  ];

  return (
    <>
      <CrudSection
        title="Νέο έργο"
        listTitle="Έργα"
        path="/projects"
        blocker={clients.length ? null : "Πρόσθεσε πρώτα έναν πελάτη."}
        fields={fields}
        rows={projects}
        onChange={reload}
        columns={[
          { label: "Όνομα", render: (p) => p.name },
          { label: "Πελάτης", render: (p) => clientNames[p.client_id] ?? "-" },
          { label: "Τοποθεσία", render: (p) => dash(p.location) },
          { label: "Έναρξη", render: (p) => dash(p.start_date) },
          { label: "Κατάσταση", render: (p) => dash(p.status) },
          { label: "Προϋπολογισμός", num: true, render: (p) => money(p.budget) },
          { label: "Ολοκλήρωση", render: (p) => dash(p.end_date) },
          { label: "Εργάσιμες μέρες", num: true, render: (p) => dash(p.working_days) },
        ]}
      />

      <Card title="Ζωντανός προϋπολογισμός ανά έργο">
        {financials.length
          ? financials.map((pf) => <BudgetItem key={pf.project_id} pf={pf} />)
          : <Notice>Δεν υπάρχουν έργα ακόμα.</Notice>}
      </Card>
    </>
  );
}
