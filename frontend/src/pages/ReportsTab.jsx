import { useState } from "react";
import { api } from "../api.js";
import { DonutChart, GroupedBarChart } from "../components/charts.jsx";
import { Card, DataTable, Loading, Metric, Notice } from "../components/ui.jsx";
import { money, MONTH_NAMES, useLoad } from "../lib.js";

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = [3, 2, 1, 0].map((back) => CURRENT_YEAR - back);
const SHORT_MONTHS = ["Ιαν", "Φεβ", "Μαρ", "Απρ", "Μάι", "Ιούν", "Ιούλ", "Αύγ", "Σεπ", "Οκτ", "Νοέ", "Δεκ"];

const marginText = (pct) => `${pct.toFixed(1)}% περιθώριο`;
const profitClass = (value) => (value < 0 ? "neg" : "pos");

// Πού πήγε ο τζίρος του μήνα: έξοδα, ημερομίσθια, φόροι και ό,τι έμεινε ως κέρδος
function TurnoverSplit({ monthly }) {
  if (!monthly.turnover) return <Notice>Δεν υπάρχει τζίρος αυτόν τον μήνα.</Notice>;

  const slices = [
    { label: "Έξοδα", value: monthly.expenses_total, color: "#2563eb" },
    { label: "Ημερομίσθια", value: monthly.wages_total, color: "#9333ea" },
    { label: "ΦΠΑ", value: monthly.vat_due, color: "#ca8a04" },
    { label: "Λοιπές φορολογίες", value: monthly.other_taxes, color: "#64748b" },
    { label: "Καθαρά κέρδη", value: Math.max(monthly.net_profit, 0), color: "#16a34a" },
  ].filter((slice) => slice.value > 0);

  return (
    <>
      <DonutChart slices={slices} centerTop={money(monthly.turnover)} centerBottom="τζίρος" />
      {monthly.net_profit < 0 && (
        <Notice kind="error">
          Τα έξοδα ξεπερνούν τον τζίρο αυτόν τον μήνα (ζημιά {money(-monthly.net_profit)}). Τα ποσοστά υπολογίζονται επί των συνολικών εξόδων.
        </Notice>
      )}
    </>
  );
}

export default function ReportsTab() {
  const [year, setYear] = useState(CURRENT_YEAR);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [projectId, setProjectId] = useState(null); // null = σύνολο, όλα τα έργα

  const projectQuery = projectId ? `&project_id=${projectId}` : "";
  const { data, error } = useLoad(() => Promise.all([
    api.get("/projects"),
    api.get(`/reports/monthly?year=${year}&month=${month}${projectQuery}`),
    api.get(`/reports/yearly?year=${year}${projectQuery}`),
    api.get(`/reports/expense-breakdown?year=${year}${projectQuery}`),
  ]), [year, month, projectId]);
  if (!data) return <Loading error={error} />;

  const [projects, monthly, yearly, breakdown] = data;
  const totals = yearly.totals;
  const hasYearActivity = totals.turnover > 0 || totals.expenses_total > 0 || totals.wages_total > 0;
  const selectedProject = projects.find((p) => p.id === projectId);
  const scopeSuffix = selectedProject ? ` — ${selectedProject.name}` : "";

  return (
    <>
      <Card>
        <label className="field" style={{ maxWidth: 320 }}>
          Έργο
          <select
            value={projectId ?? ""}
            onChange={(e) => setProjectId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Σύνολο (όλα τα έργα)</option>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
        {selectedProject && (
          <p className="caption" style={{ marginTop: 10, marginBottom: 0 }}>
            Οι «Λοιπές φορολογίες» αφορούν όλη την επιχείρηση, όχι συγκεκριμένο έργο — γι&apos;
            αυτό εδώ εμφανίζονται πάντα μηδέν.
          </p>
        )}
      </Card>

      <Card title={`Μηνιαία αναφορά${scopeSuffix}`}>
        <div className="form-grid" style={{ marginBottom: 16, maxWidth: 460 }}>
          <label className="field">
            Έτος
            <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
              {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </label>
          <label className="field">
            Μήνας
            <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
              {MONTH_NAMES.map((name, i) => <option key={name} value={i + 1}>{name}</option>)}
            </select>
          </label>
        </div>
        <div className="metrics">
          <Metric label="Τζίρος" value={money(monthly.turnover)} />
          <Metric label="Έξοδα" value={money(monthly.expenses_total)} />
          <Metric label="Ημερομίσθια" value={money(monthly.wages_total)} />
          <Metric label="ΦΠΑ προς απόδοση" value={money(monthly.vat_due)} />
          <Metric label="Λοιπές φορολογίες" value={money(monthly.other_taxes)} />
          <Metric
            label="Καθαρά κέρδη" value={money(monthly.net_profit)}
            sub={marginText(monthly.profit_margin_pct)} className={profitClass(monthly.net_profit)}
          />
        </div>
        <h3>Πού πηγαίνει ο τζίρος ({MONTH_NAMES[month - 1]})</h3>
        <TurnoverSplit monthly={monthly} />
      </Card>

      <Card title={`Ετήσια αναφορά ${year}${scopeSuffix}`}>
        <div className="metrics">
          <Metric label="Τζίρος έτους" value={money(totals.turnover)} />
          <Metric label="Σύνολο εξόδων + ημερομισθίων" value={money(totals.expenses_total + totals.wages_total)} />
          <Metric
            label="Καθαρά κέρδη έτους" value={money(totals.net_profit)}
            sub={marginText(totals.profit_margin_pct)} className={profitClass(totals.net_profit)}
          />
        </div>

        <h3>Τζίρος και έξοδα ανά μήνα</h3>
        {hasYearActivity ? (
          <GroupedBarChart
            labels={SHORT_MONTHS}
            series={[
              { name: "Τζίρος", color: "#ea580c", values: yearly.months.map((m) => m.turnover) },
              { name: "Έξοδα + ημερομίσθια", color: "#2563eb", values: yearly.months.map((m) => m.expenses_total + m.wages_total) },
            ]}
          />
        ) : <Notice>Δεν υπάρχουν κινήσεις για αυτό το έτος{scopeSuffix}.</Notice>}

        <h3 style={{ marginTop: 22 }}>Ανά μήνα</h3>
        <DataTable
          rows={yearly.months}
          columns={[
            { label: "Μήνας", render: (m) => MONTH_NAMES[m.month - 1] },
            { label: "Τζίρος", num: true, render: (m) => money(m.turnover) },
            { label: "Έξοδα", num: true, render: (m) => money(m.expenses_total) },
            { label: "Ημερομίσθια", num: true, render: (m) => money(m.wages_total) },
            { label: "ΦΠΑ", num: true, render: (m) => money(m.vat_due) },
            { label: "Καθαρά κέρδη", num: true, render: (m) => money(m.net_profit) },
            { label: "Περιθώριο", num: true, render: (m) => `${m.profit_margin_pct.toFixed(1)}%` },
          ]}
        />
      </Card>

      <Card title={`Κατανομή εξόδων ανά κατηγορία (${year})${scopeSuffix}`}>
        {breakdown.length ? (
          <DonutChart
            slices={breakdown.map((b) => ({ label: b.category, value: b.amount }))}
            centerTop={money(breakdown.reduce((sum, b) => sum + b.amount, 0))}
            centerBottom="σύνολο εξόδων"
          />
        ) : <Notice>Δεν υπάρχουν έξοδα καταχωρημένα για αυτό το έτος{scopeSuffix}.</Notice>}
      </Card>
    </>
  );
}
