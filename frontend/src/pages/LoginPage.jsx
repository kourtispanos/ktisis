import { useState } from "react";
import { api, setToken } from "../api.js";
import { Form, useToast } from "../components/forms.jsx";
import { Logo } from "../components/icons.jsx";
import { Notice } from "../components/ui.jsx";

const LOGIN_FIELDS = [
  { name: "username", label: "Όνομα χρήστη", required: true },
  { name: "password", label: "Κωδικός", type: "password", required: true },
];

const SIGNUP_FIELDS = [
  ...LOGIN_FIELDS,
  { name: "confirm", label: "Επιβεβαίωση κωδικού", type: "password", required: true },
];

export default function LoginPage({ message, onLogin }) {
  const toast = useToast();
  const [mode, setMode] = useState("login");

  const login = async (values) => {
    const result = await api.post("/auth/login", values);
    setToken(result.token);
    onLogin(result.username);
  };

  const signup = async (values) => {
    if (values.password !== values.confirm) {
      toast("Οι κωδικοί δεν ταιριάζουν", "error");
      return;
    }
    await api.post("/auth/signup", { username: values.username, password: values.password });
    toast("Ο λογαριασμός δημιουργήθηκε! Μπορείς να συνδεθείς.");
    setMode("login");
  };

  return (
    <div className="login-page">
      <div className="login-brand">
        <Logo size={56} />
        <h1>Ktisis</h1>
        <p>Πελάτες, έργα, προσωπικό και οικονομικά της εργολαβίας σου, σε ένα μέρος.</p>
        <ul>
          <li>Ζωντανός προϋπολογισμός ανά έργο</li>
          <li>ΦΠΑ, τιμολόγια και μηνιαίες αναφορές</li>
          <li>Υπενθυμίσεις για ΚΤΕΟ, ασφάλειες και προθεσμίες</li>
        </ul>
      </div>

      <div className="login-panel">
        <div className="login-box">
          <h2>{mode === "login" ? "Καλώς ήρθες" : "Νέος λογαριασμός"}</h2>
          <p className="caption">
            {mode === "login" ? "Συνδέσου για να συνεχίσεις." : "Φτιάξε λογαριασμό για να ξεκινήσεις."}
          </p>
          {message && <Notice kind="warn">{message}</Notice>}
          <div className="seg">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Σύνδεση</button>
            <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>Εγγραφή</button>
          </div>
          {mode === "login"
            ? <Form key="login" fields={LOGIN_FIELDS} submitLabel="Σύνδεση" onSubmit={login} />
            : <Form key="signup" fields={SIGNUP_FIELDS} submitLabel="Δημιουργία λογαριασμού" onSubmit={signup} />}
        </div>
      </div>
    </div>
  );
}
