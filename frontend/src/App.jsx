import { useEffect, useMemo, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function fetchStatementsPaged({ size = 50 } = {}) {
  // Pull all pages from our backend (which mirrors ORKG’s pagination).
  let page = 0;
  let all = [];
  // First call to know totals
  const first = await fetch(
    `${API_BASE}/api/statements?page=${page}&size=${size}`
  );
  if (!first.ok) throw new Error(`HTTP ${first.status}`);
  let data = await first.json();
  all = all.concat(data.content || []);
  const totalPages = data?.page?.total_pages ?? 0;

  while (page + 1 < totalPages) {
    page += 1;
    const res = await fetch(
      `${API_BASE}/api/statements?page=${page}&size=${size}`
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const d = await res.json();
    all = all.concat(d.content || []);
  }
  return all;
}

function buildHistogram(rows) {
  // Same bins as your UI: 0–10, 10–20, ..., 190–200, 200+
  const cap = 200;
  const binSize = 10;
  const numBins = Math.floor(cap / binSize);
  const bins = new Array(numBins).fill(0);
  let overflow = 0;

  for (const r of rows) {
    const c = Number(r.count || 0);
    if (c >= cap) overflow++;
    else bins[Math.floor(c / binSize)]++;
  }

  const labels = bins.map((_, i) => `${i * binSize}–${(i + 1) * binSize}`);
  labels.push(`${cap}+`);
  const dataPoints = [...bins, overflow];

  return {
    labels,
    datasets: [
      {
        label: "Papers",
        data: dataPoints,
        backgroundColor: "rgba(75,192,192,0.6)",
        borderColor: "rgba(75,192,192,1)",
        borderWidth: 1,
      },
    ],
  };
}

export default function App() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setError("");
        const all = await fetchStatementsPaged({ size: 5000 });
        setRows(all);
      } catch (e) {
        setError(e.message || String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const histogram = useMemo(() => buildHistogram(rows), [rows]);

  const avg = useMemo(() => {
    if (!rows.length) return 0;
    return (rows.reduce((s, r) => s + Number(r.count || 0), 0) / rows.length).toFixed(2);
  }, [rows]);

  const median = useMemo(() => {
    if (!rows.length) return 0;
    const arr = rows.map(r => Number(r.count || 0)).sort((a,b)=>a-b);
    const mid = Math.floor(arr.length/2);
    return arr.length % 2 ? arr[mid] : ((arr[mid-1]+arr[mid])/2).toFixed(2);
  }, [rows]);

  if (loading) return <div style={{ padding: 20 }}>Loading…</div>;
  if (error) return <div style={{ padding: 20, color: "crimson" }}>Error: {error}</div>;

  return (
    <div style={{ maxWidth: 980, margin: "24px auto", padding: "0 16px" }}>
      <h1 style={{ marginBottom: 8 }}>Statements per Paper — Histogram</h1>
      <div style={{ color: "#555", marginBottom: 16 }}>
        Loaded <strong>{rows.length}</strong> papers · Avg: <strong>{avg}</strong> · Median: <strong>{median}</strong>
      </div>
      <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <Bar
          data={histogram}
          options={{
            responsive: true,
            plugins: {
              legend: { display: false },
              title: { display: true, text: "Distribution of Statements per Paper" },
            },
            scales: {
              x: {
                title: { display: true, text: "Number of statements" },
                ticks: { autoSkip: false, maxRotation: 45, minRotation: 30 },
              },
              y: { title: { display: true, text: "Number of papers" } },
            },
          }}
        />
      </div>
      <div style={{ marginTop: 16, fontSize: 12, color: "#777" }}>
        Data source: FastAPI at <code>{API_BASE}</code> (backed by Postgres via dlt)
      </div>
    </div>
  );
}