import { api } from "../api.js";
import { CrudSection, Loading } from "../components/ui.jsx";
import { dash, money, nameMap, today, toOptions, useLoad } from "../lib.js";

const WORKER_FIELDS = [
  { name: "name", label: "Όνομα εργάτη", required: true },
  { name: "specialty", label: "Ειδικότητα" },
  { name: "daily_wage", label: "Ημερομίσθιο (€)", type: "number", min: 0, step: 5 },
];

export default function StaffTab() {
  const { data, error, reload } = useLoad(() => Promise.all([
    api.get("/workers"), api.get("/workers/totals/all"), api.get("/projects"), api.get("/wage-entries"),
  ]));
  if (!data) return <Loading error={error} />;

  const [workers, totals, projects, wages] = data;
  const totalsById = Object.fromEntries(totals.map((t) => [t.id, t]));
  const workerNames = nameMap(workers);
  const projectNames = nameMap(projects);
  const dailyWageById = Object.fromEntries(workers.map((w) => [w.id, w.daily_wage || 0]));

  const wageFields = [
    { name: "worker_id", label: "Εργάτης", type: "select", required: true, options: toOptions(workers, (w) => w.name) },
    { name: "project_id", label: "Έργο", type: "select", required: true, options: toOptions(projects, (p) => p.name) },
    { name: "work_date", label: "Ημερομηνία", type: "date", required: true, default: today },
    { name: "days", label: "Ημέρες", type: "number", required: true, min: 0, step: 0.5, default: 1 },
  ];

  return (
    <div className="columns">
      <CrudSection
        title="Νέος εργάτης"
        listTitle="Προσωπικό - σύνολα"
        path="/workers"
        fields={WORKER_FIELDS}
        rows={workers}
        onChange={reload}
        columns={[
          { label: "Όνομα", render: (w) => w.name },
          { label: "Ειδικότητα", render: (w) => dash(w.specialty) },
          { label: "Ημερομίσθιο", num: true, render: (w) => money(w.daily_wage) },
          { label: "Σύνολο ημερών", num: true, render: (w) => totalsById[w.id]?.total_days ?? 0 },
          { label: "Σύνολο αμοιβής", num: true, render: (w) => money(totalsById[w.id]?.total_amount ?? 0) },
        ]}
      />

      <CrudSection
        title="Νέο ημερομίσθιο"
        listTitle="Ημερομίσθια"
        path="/wage-entries"
        blocker={workers.length && projects.length ? null : "Χρειάζεσαι τουλάχιστον έναν εργάτη και ένα έργο."}
        fields={wageFields}
        rows={wages}
        onChange={reload}
        beforeList={<p className="caption">Το ποσό υπολογίζεται αυτόματα: ημερομίσθιο εργάτη × ημέρες</p>}
        // Το ποσό δεν το πληκτρολογεί ο χρήστης - προκύπτει από το ημερομίσθιο του εργάτη
        toPayload={(values) => ({ ...values, amount: (dailyWageById[values.worker_id] || 0) * values.days })}
        columns={[
          { label: "Εργάτης", render: (e) => workerNames[e.worker_id] ?? "-" },
          { label: "Έργο", render: (e) => projectNames[e.project_id] ?? "-" },
          { label: "Ημερομηνία", render: (e) => e.work_date },
          { label: "Ημέρες", num: true, render: (e) => e.days },
          { label: "Ποσό", num: true, render: (e) => money(e.amount) },
        ]}
      />
    </div>
  );
}
