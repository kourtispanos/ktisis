import { createContext, useCallback, useContext, useState } from "react";
import { today } from "../lib.js";

// ---------- Ειδοποιήσεις ----------

const ToastContext = createContext(() => {});

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const toast = useCallback((message, type = "success") => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { id, message, type }]);
    setTimeout(
      () => setToasts((current) => current.filter((t) => t.id !== id)),
      type === "error" ? 6000 : 3000,
    );
  }, []);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div id="toasts">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>{t.message}</div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);


// ---------- Φόρμες ----------

// Τα πεδία περιγράφονται δηλωτικά: { name, label, type, required, wide, options, ... }.
// Η φόρμα κρατά τις τιμές σε state και στο submit τις μετατρέπει σε μορφή έτοιμη για το API.

function initialValue(spec, initial) {
  const stored = initial?.[spec.name];
  const fallback = typeof spec.default === "function" ? spec.default() : spec.default;

  if (spec.type === "optdate") return stored ?? null;
  if (spec.type === "checkbox") return Boolean(stored ?? fallback);
  if (spec.type === "select") {
    const options = spec.options || [];
    const wanted = stored ?? fallback;
    if (wanted != null && options.some((o) => String(o.value) === String(wanted))) return wanted;
    return spec.allowEmpty ? null : (options[0]?.value ?? null);
  }
  return stored ?? fallback ?? "";
}

function toApiValue(spec, value) {
  switch (spec.type) {
    case "number":
      return value === "" ? null : parseFloat(value);
    case "checkbox":
    case "select":
    case "optdate":
    case "password":
      return value;
    default: {
      const trimmed = String(value).trim();
      return trimmed === "" ? null : trimmed;
    }
  }
}

function Field({ spec, value, onChange }) {
  const cls = `field${spec.type === "checkbox" ? " check" : ""}${spec.wide ? " wide" : ""}`;

  if (spec.type === "checkbox") {
    return (
      <label className={cls}>
        <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
        {spec.label}
      </label>
    );
  }

  if (spec.type === "select") {
    const options = spec.options || [];
    const index = options.findIndex((o) => String(o.value) === String(value));
    return (
      <label className={cls}>
        {spec.label}
        <select
          value={value == null || index < 0 ? "" : String(index)}
          onChange={(e) => onChange(e.target.value === "" ? null : options[Number(e.target.value)].value)}
        >
          {spec.allowEmpty && <option value="">{spec.emptyLabel || "-"}</option>}
          {options.map((o, i) => <option key={i} value={String(i)}>{o.label}</option>)}
        </select>
      </label>
    );
  }

  if (spec.type === "optdate") {
    return (
      <div className={`field ${spec.wide ? "wide" : ""}`}>
        <label className="field check">
          <input
            type="checkbox"
            checked={value != null}
            onChange={(e) => onChange(e.target.checked ? today() : null)}
          />
          {spec.label}
        </label>
        {value != null && <input type="date" value={value} onChange={(e) => onChange(e.target.value || null)} />}
      </div>
    );
  }

  if (spec.type === "textarea") {
    return (
      <label className={cls}>
        {spec.label}
        <textarea rows={2} value={value} onChange={(e) => onChange(e.target.value)} />
      </label>
    );
  }

  return (
    <label className={cls}>
      {spec.label}
      <input
        type={spec.type || "text"}
        step={spec.step}
        min={spec.min}
        placeholder={spec.placeholder}
        autoComplete={spec.type === "password" ? "off" : undefined}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}

export function Form({ fields, initial, submitLabel, onSubmit, danger = false, children }) {
  const toast = useToast();
  const [values, setValues] = useState(() =>
    Object.fromEntries(fields.map((spec) => [spec.name, initialValue(spec, initial)])));
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {};
    for (const spec of fields) {
      payload[spec.name] = toApiValue(spec, values[spec.name]);
      if (spec.required && (payload[spec.name] == null || payload[spec.name] === "")) {
        toast(`Το πεδίο «${spec.label}» είναι υποχρεωτικό`, "error");
        return;
      }
    }
    setBusy(true);
    try {
      await onSubmit(payload);
    } catch (error) {
      toast(error.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-grid">
        {fields.map((spec) => (
          <Field
            key={spec.name}
            spec={spec}
            value={values[spec.name]}
            onChange={(value) => setValues((current) => ({ ...current, [spec.name]: value }))}
          />
        ))}
      </div>
      <div className="form-actions">
        <button type="submit" className={danger ? "primary danger-solid" : "primary"} disabled={busy}>{submitLabel}</button>
        {children}
      </div>
    </form>
  );
}
