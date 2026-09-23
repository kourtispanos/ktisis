import { useState } from "react";
import { api } from "../api.js";
import { Card, CrudSection, Loading, Notice } from "../components/ui.jsx";
import { dash, MONTH_NAMES, today, useLoad } from "../lib.js";

const WEEKDAYS = ["Δευ", "Τρι", "Τετ", "Πεμ", "Παρ", "Σαβ", "Κυρ"];
const STATUS_ICONS = { "Πέρασε": "🔴", "Σήμερα": "🟠", "Σύντομα": "🟡" };
const pad = (n) => String(n).padStart(2, "0");

function MonthGrid({ year, month, selected, eventDates, onSelect, onShift }) {
  const offset = (new Date(year, month - 1, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(year, month, 0).getDate();
  const todayStr = today();

  const days = [];
  for (let i = 0; i < offset; i++) days.push(<div key={`blank-${i}`} className="cal-day blank" />);
  for (let day = 1; day <= daysInMonth; day++) {
    const date = `${year}-${pad(month)}-${pad(day)}`;
    const classes = ["cal-day", date === todayStr && "today", date === selected && "selected"].filter(Boolean);
    days.push(
      <button key={date} type="button" className={classes.join(" ")} onClick={() => onSelect(date)}>
        <span>{day}</span>
        {eventDates.has(date) && <span className="dot">• υπενθύμιση</span>}
      </button>,
    );
  }

  return (
    <Card>
      <div className="cal-head">
        <button onClick={() => onShift(-1)}>◀ Προηγούμενος</button>
        <h3>{MONTH_NAMES[month - 1]} {year}</h3>
        <button onClick={() => onShift(1)}>Επόμενος ▶</button>
      </div>
      <div className="cal-grid">
        {WEEKDAYS.map((wd) => <div key={wd} className="cal-wd">{wd}</div>)}
        {days}
      </div>
    </Card>
  );
}

export default function CalendarTab({ meta }) {
  const now = new Date();
  const [view, setView] = useState({ year: now.getFullYear(), month: now.getMonth() + 1 });
  const [selected, setSelected] = useState(today());

  const { data, error, reload } = useLoad(() =>
    Promise.all([api.get("/events"), api.get("/events/upcoming/all")]));
  if (!data) return <Loading error={error} />;

  const [events, upcoming] = data;
  const eventDates = new Set(events.map((e) => e.event_date));
  const dayEvents = events.filter((e) => e.event_date === selected);

  const shift = (delta) => setView(({ year, month }) => {
    const next = month + delta;
    if (next < 1) return { year: year - 1, month: 12 };
    if (next > 12) return { year: year + 1, month: 1 };
    return { year, month: next };
  });

  const fields = [
    { name: "event_date", label: "Ημερομηνία", type: "date", required: true, default: today },
    { name: "title", label: "Τίτλος", required: true },
    { name: "event_type", label: "Τύπος", type: "select", options: meta.event_types.map((t) => ({ value: t, label: t })) },
    { name: "notes", label: "Σημειώσεις", type: "textarea", wide: true },
  ];

  return (
    <>
      <MonthGrid
        year={view.year} month={view.month} selected={selected}
        eventDates={eventDates} onSelect={setSelected} onShift={shift}
      />

      <Card title={`📅 ${selected}`}>
        {dayEvents.length ? (
          <ul className="plain">
            {dayEvents.map((e) => (
              <li key={e.id}>
                <strong>{e.title}</strong> ({dash(e.event_type)}){e.notes ? ` - ${e.notes}` : ""}
              </li>
            ))}
          </ul>
        ) : <div className="caption">Καμία υπενθύμιση αυτή τη μέρα.</div>}
      </Card>

      <Card title="Επερχόμενα">
        {upcoming.length ? (
          <ul className="plain">
            {upcoming.map((e) => (
              <li key={e.id}>
                {STATUS_ICONS[e.status] || "⚪"} <strong>{e.title}</strong> ({dash(e.event_type)}) - {e.event_date} - {e.status}
              </li>
            ))}
          </ul>
        ) : <Notice>Καμία υπενθύμιση τις επόμενες 7 μέρες.</Notice>}
      </Card>

      <CrudSection
        key={selected}
        title="Νέα υπενθύμιση"
        listTitle="Όλες οι υπενθυμίσεις"
        path="/events"
        initial={{ event_date: selected }}
        fields={fields}
        rows={events}
        onChange={reload}
        columns={[
          { label: "Ημερομηνία", render: (e) => e.event_date },
          { label: "Τίτλος", render: (e) => e.title },
          { label: "Τύπος", render: (e) => dash(e.event_type) },
          { label: "Σημειώσεις", render: (e) => dash(e.notes) },
        ]}
      />
    </>
  );
}
