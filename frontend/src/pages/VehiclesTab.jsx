import { api } from "../api.js";
import { Badge, CrudSection, Loading } from "../components/ui.jsx";
import { dash, today, useLoad } from "../lib.js";

const FIELDS = [
  { name: "name", label: "Όνομα / Τύπος οχήματος", required: true },
  { name: "license_plate", label: "Πινακίδα" },
  { name: "insurance_expiry", label: "Λήξη ασφάλειας", type: "date", default: today },
  { name: "kteo_expiry", label: "Λήξη ΚΤΕΟ", type: "date", default: today },
  { name: "road_tax_expiry", label: "Λήξη τελών κυκλοφορίας", type: "date", default: today },
  { name: "last_service_date", label: "Έχει γίνει σέρβις;", type: "optdate" },
  { name: "service_notes", label: "Σημειώσεις σέρβις (τι έγινε)", type: "textarea", wide: true },
  { name: "notes", label: "Γενικές σημειώσεις", wide: true },
];

export default function VehiclesTab() {
  const { data: vehicles, error, reload } = useLoad(() => api.get("/vehicles"));
  if (!vehicles) return <Loading error={error} />;

  return (
    <CrudSection
      title="Νέο όχημα"
      listTitle="Οχήματα"
      path="/vehicles"
      fields={FIELDS}
      rows={vehicles}
      onChange={reload}
      columns={[
        { label: "Όνομα", render: (v) => v.name },
        { label: "Πινακίδα", render: (v) => dash(v.license_plate) },
        { label: "Ασφάλεια λήγει", render: (v) => dash(v.insurance_expiry) },
        { label: "Ασφάλεια", render: (v) => <Badge text={v.insurance_status} /> },
        { label: "ΚΤΕΟ λήγει", render: (v) => dash(v.kteo_expiry) },
        { label: "ΚΤΕΟ", render: (v) => <Badge text={v.kteo_status} /> },
        { label: "Τέλη λήγουν", render: (v) => dash(v.road_tax_expiry) },
        { label: "Τέλη", render: (v) => <Badge text={v.road_tax_status} /> },
        { label: "Τελευταίο σέρβις", render: (v) => dash(v.last_service_date) },
        { label: "Σημειώσεις σέρβις", render: (v) => dash(v.service_notes) },
        { label: "Γενικές σημειώσεις", render: (v) => dash(v.notes) },
      ]}
    />
  );
}
