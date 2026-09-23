import { api } from "../api.js";
import { CrudSection, Loading } from "../components/ui.jsx";
import { dash, money, useLoad } from "../lib.js";

const FIELDS = [
  { name: "name", label: "Όνομα", required: true },
  { name: "phone", label: "Τηλέφωνο" },
  { name: "email", label: "Email" },
  { name: "address", label: "Διεύθυνση" },
];

export default function ClientsTab() {
  const { data, error, reload } = useLoad(() =>
    Promise.all([api.get("/clients"), api.get("/clients/balances/all")]));
  if (!data) return <Loading error={error} />;

  const [clients, balances] = data;
  const balanceById = Object.fromEntries(balances.map((b) => [b.id, b]));

  return (
    <CrudSection
      title="Νέος πελάτης"
      listTitle="Πελάτες - Πληρωμές & Υπόλοιπο"
      path="/clients"
      fields={FIELDS}
      rows={clients}
      onChange={reload}
      columns={[
        { label: "Πελάτης", render: (c) => c.name },
        { label: "Τηλέφωνο", render: (c) => dash(c.phone) },
        { label: "Email", render: (c) => dash(c.email) },
        { label: "Διεύθυνση", render: (c) => dash(c.address) },
        { label: "Προϋπολογισμός έργων", num: true, render: (c) => money(balanceById[c.id]?.total_budget ?? 0) },
        { label: "Πληρωμένο", num: true, render: (c) => money(balanceById[c.id]?.total_paid ?? 0) },
        { label: "Υπόλοιπο", num: true, render: (c) => money(balanceById[c.id]?.balance ?? 0) },
      ]}
    />
  );
}
