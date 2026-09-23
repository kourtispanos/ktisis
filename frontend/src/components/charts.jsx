import { money } from "../lib.js";

// Γραφήματα σε καθαρό SVG - δεν χρειάζεται εξωτερική βιβλιοθήκη

const PALETTE = ["#ea580c", "#2563eb", "#16a34a", "#9333ea", "#0891b2", "#ca8a04", "#db2777", "#64748b", "#84cc16", "#f43f5e"];
export const chartColor = (index) => PALETTE[index % PALETTE.length];

const percentText = (value, total) => `${total ? ((value / total) * 100).toFixed(1) : "0.0"}%`;

function Donut({ slices, total, centerTop, centerBottom }) {
  const radius = 70;
  const stroke = 30;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <svg viewBox="0 0 200 200" className="donut" role="img" aria-label={centerBottom}>
      <circle cx="100" cy="100" r={radius} fill="none" stroke="var(--border)" strokeWidth={stroke} />
      {slices.map((slice) => {
        const length = total ? (slice.value / total) * circumference : 0;
        const circle = (
          <circle
            key={slice.label}
            cx="100" cy="100" r={radius} fill="none"
            stroke={slice.color} strokeWidth={stroke}
            strokeDasharray={`${length} ${circumference - length}`}
            strokeDashoffset={-offset}
            transform="rotate(-90 100 100)"
          >
            <title>{`${slice.label}: ${money(slice.value)} (${percentText(slice.value, total)})`}</title>
          </circle>
        );
        offset += length;
        return circle;
      })}
      <text x="100" y="98" textAnchor="middle" className="donut-top">{centerTop}</text>
      <text x="100" y="118" textAnchor="middle" className="donut-bottom">{centerBottom}</text>
    </svg>
  );
}

// Στρογγυλό γράφημα με υπόμνημα (χρώμα, όνομα, ποσό, ποσοστό)
// slices: [{ label, value, color? }]
export function DonutChart({ slices, centerTop, centerBottom }) {
  const colored = slices.map((slice, i) => ({ ...slice, color: slice.color || chartColor(i) }));
  const total = colored.reduce((sum, slice) => sum + slice.value, 0);

  return (
    <div className="chart-row">
      <Donut slices={colored} total={total} centerTop={centerTop} centerBottom={centerBottom} />
      <ul className="legend">
        {colored.map((slice) => (
          <li key={slice.label}>
            <span className="dot" style={{ background: slice.color }} />
            <span className="legend-label">{slice.label}</span>
            <span className="legend-amount">{money(slice.value)}</span>
            <strong className="legend-pct">{percentText(slice.value, total)}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}

function niceMax(value) {
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const n = value / magnitude;
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * magnitude;
}

const compact = new Intl.NumberFormat("el-GR", { notation: "compact", maximumFractionDigits: 1 });

// Μπάρες ανά κατηγορία (π.χ. μήνα). series: [{ name, color, values: [...] }]
export function GroupedBarChart({ labels, series }) {
  const width = 720;
  const height = 260;
  const pad = { left: 52, right: 8, top: 12, bottom: 30 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const max = niceMax(Math.max(1, ...series.flatMap((s) => s.values)));
  const band = plotW / labels.length;
  const barW = (band * 0.72) / series.length;
  const y = (value) => pad.top + plotH - (value / max) * plotH;

  return (
    <div>
      <svg viewBox={`0 0 ${width} ${height}`} className="bars" role="img">
        {[0, 1, 2, 3, 4].map((i) => {
          const value = (max / 4) * i;
          return (
            <g key={i}>
              <line x1={pad.left} x2={width - pad.right} y1={y(value)} y2={y(value)} className="grid-line" />
              <text x={pad.left - 8} y={y(value) + 4} textAnchor="end" className="axis-text">{compact.format(value)}</text>
            </g>
          );
        })}
        {labels.map((label, i) => {
          const groupX = pad.left + i * band + (band - barW * series.length) / 2;
          return (
            <g key={label}>
              {series.map((s, j) => (
                <rect
                  key={s.name}
                  x={groupX + j * barW} y={y(s.values[i])}
                  width={barW - 1} height={pad.top + plotH - y(s.values[i])}
                  rx="2" fill={s.color}
                >
                  <title>{`${label} - ${s.name}: ${money(s.values[i])}`}</title>
                </rect>
              ))}
              <text x={pad.left + i * band + band / 2} y={height - 10} textAnchor="middle" className="axis-text">{label}</text>
            </g>
          );
        })}
      </svg>
      <div className="bar-legend">
        {series.map((s) => (
          <span key={s.name}><span className="dot" style={{ background: s.color }} />{s.name}</span>
        ))}
      </div>
    </div>
  );
}
