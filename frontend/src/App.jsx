import { useEffect, useState } from "react";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api.js";
import { Form, useToast } from "./components/forms.jsx";
import { Icon, Logo } from "./components/icons.jsx";
import { Dialog, Loading, Notice } from "./components/ui.jsx";
import CalendarTab from "./pages/CalendarTab.jsx";
import ClientsTab from "./pages/ClientsTab.jsx";
import FinanceTab from "./pages/FinanceTab.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ProjectsTab from "./pages/ProjectsTab.jsx";
import ReportsTab from "./pages/ReportsTab.jsx";
import StaffTab from "./pages/StaffTab.jsx";
import TaxesTab from "./pages/TaxesTab.jsx";
import VehiclesTab from "./pages/VehiclesTab.jsx";
import WeatherTab from "./pages/WeatherTab.jsx";

const TABS = [
  { id: "clients", label: "Πελάτες", icon: "users", hint: "Στοιχεία πελατών, πληρωμές και υπόλοιπα", Component: ClientsTab },
  { id: "projects", label: "Έργα", icon: "briefcase", hint: "Έργα, προϋπολογισμός και πορεία δαπανών", Component: ProjectsTab },
  { id: "staff", label: "Προσωπικό", icon: "hardhat", hint: "Εργάτες και καταγραφή ημερομισθίων", Component: StaffTab },
  { id: "finance", label: "Έξοδα & Έσοδα", icon: "wallet", hint: "Δαπάνες και εισπράξεις ανά έργο", Component: FinanceTab },
  { id: "taxes", label: "Φορολογίες", icon: "receipt", hint: "ΦΠΑ, φορολογικές υποχρεώσεις και τιμολόγια", Component: TaxesTab },
  { id: "weather", label: "Καιρός", icon: "weather", hint: "Τρέχων καιρός και πρόγνωση για τα εργοτάξια", Component: WeatherTab },
  { id: "calendar", label: "Ημερολόγιο", icon: "calendar", hint: "Ραντεβού, προθεσμίες και υπενθυμίσεις", Component: CalendarTab },
  { id: "vehicles", label: "Οχήματα", icon: "truck", hint: "Ασφάλεια, ΚΤΕΟ, τέλη κυκλοφορίας και σέρβις", Component: VehiclesTab },
  { id: "reports", label: "Αναφορές", icon: "chart", hint: "Τζίρος, έξοδα και καθαρά κέρδη", Component: ReportsTab },
];

function DeleteAccountDialog({ username, onClose, onDeleted }) {
  return (
    <Dialog title="Διαγραφή λογαριασμού" onClose={onClose}>
      <Notice kind="error">
        Ο λογαριασμός «{username}» θα διαγραφεί οριστικά. Τα δεδομένα της εργολαβίας
        (πελάτες, έργα, οικονομικά κ.λπ.) δεν διαγράφονται.
      </Notice>
      <Form
        fields={[{ name: "password", label: "Γράψε τον κωδικό σου για επιβεβαίωση", type: "password", required: true }]}
        submitLabel="Διαγραφή λογαριασμού"
        danger
        onSubmit={async (values) => {
          await api.post("/auth/delete-account", values);
          onDeleted();
        }}
      >
        <button type="button" onClick={onClose}>Άκυρο</button>
      </Form>
    </Dialog>
  );
}

function Dashboard({ username, onLogout }) {
  const [activeId, setActiveId] = useState(TABS[0].id);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    api.get("/meta").then(setMeta, (e) => setError(e.message));
  }, []);

  const logout = async () => {
    try { await api.post("/auth/logout"); } catch { /* ο server μπορεί να έχει επανεκκινήσει */ }
    onLogout();
  };

  const { Component, label, hint } = TABS.find((t) => t.id === activeId);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Logo />
          <div>
            <strong>Ktisis</strong>
            <span>Διαχείριση εργολαβίας</span>
          </div>
        </div>

        <nav className="nav">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`nav-item${tab.id === activeId ? " active" : ""}`}
              onClick={() => setActiveId(tab.id)}
            >
              <Icon name={tab.icon} />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="avatar">{username.charAt(0).toUpperCase()}</div>
          <div className="who">
            <span>Συνδεδεμένος</span>
            <strong>{username}</strong>
          </div>
          <button className="icon-btn" title="Διαγραφή λογαριασμού" onClick={() => setDeleting(true)}>
            <Icon name="userx" />
          </button>
          <button className="icon-btn" title="Αποσύνδεση" onClick={logout}>
            <Icon name="logout" />
          </button>
        </div>
      </aside>

      {deleting && (
        <DeleteAccountDialog
          username={username}
          onClose={() => setDeleting(false)}
          onDeleted={() => { toast("Ο λογαριασμός διαγράφηκε"); onLogout(); }}
        />
      )}

      <main>
        <header className="page-head">
          <h2>{label}</h2>
          <p>{hint}</p>
        </header>
        {meta ? <Component key={activeId} meta={meta} /> : <Loading error={error} />}
      </main>
    </div>
  );
}

export default function App() {
  // undefined = ελέγχουμε ακόμα αν υπάρχει ενεργή σύνδεση, null = δεν είναι συνδεδεμένος
  const [username, setUsername] = useState(getToken() ? undefined : null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setMessage("Η σύνδεσή σου έληξε. Συνδέσου ξανά.");
      setUsername(null);
    });
    if (getToken()) {
      api.get("/auth/me").then(
        (me) => setUsername(me.username),
        () => { setToken(null); setUsername(null); },
      );
    }
  }, []);

  if (username === undefined) return null;
  if (username === null) {
    return <LoginPage message={message} onLogin={(name) => { setMessage(null); setUsername(name); }} />;
  }
  return <Dashboard username={username} onLogout={() => { setToken(null); setUsername(null); }} />;
}
