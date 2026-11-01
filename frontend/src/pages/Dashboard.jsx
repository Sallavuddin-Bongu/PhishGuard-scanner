import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, errorMessage } from "../api.js";
import VerdictBadge from "../components/VerdictBadge.jsx";

const COLORS = { SAFE: "#34d399", SUSPICIOUS: "#fbbf24", PHISHING: "#f87171" };

function StatCard({ label, value, tone = "" }) {
  return (
    <div className="card">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`text-3xl font-bold ${tone}`}>{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/dashboard").then((r) => setData(r.data)).catch((e) => setError(errorMessage(e)));
  }, []);

  if (error) return <div className="card text-red-300">{error}</div>;
  if (!data) return <p className="text-slate-400">Loading…</p>;

  const pieData = Object.entries(data.counts).map(([name, value]) => ({ name, value }));
  const pieTotal = pieData.reduce((sum, d) => sum + d.value, 0);
  const percentOf = (value) => (pieTotal ? ((value / pieTotal) * 100).toFixed(1) : "0.0");

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-slate-400">Your scan activity at a glance.</p>
        </div>
        <Link to="/scan" className="btn-primary">Scan a URL</Link>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Total scans" value={data.total_scans} />
        <StatCard label="Safe" value={data.counts.SAFE} tone="text-emerald-300" />
        <StatCard label="Suspicious" value={data.counts.SUSPICIOUS} tone="text-amber-300" />
        <StatCard label="Phishing" value={data.counts.PHISHING} tone="text-red-300" />
      </div>

      {data.is_empty ? (
        <div className="card text-slate-300">
          No scans yet. <Link to="/scan" className="text-brand-400">Scan your first URL</Link> and the charts will appear here.
        </div>
      ) : (
        <>
          <p className="text-sm text-slate-400">Flagged as suspicious or phishing: {data.detection_percentage}%</p>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="card h-80">
              <h2 className="mb-2 font-semibold">Verdict distribution</h2>
              <ResponsiveContainer width="100%" height="85%">
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={80}
                    label={({ name, value }) => `${name} ${percentOf(value)}%`}
                  >
                    {pieData.map((d) => <Cell key={d.name} fill={COLORS[d.name]} />)}
                  </Pie>
                  <Tooltip formatter={(value, name) => [`${value} scans (${percentOf(value)}%)`, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="card h-80">
              <h2 className="mb-2 font-semibold">Scans per day</h2>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={data.daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff22" />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="scans" fill="#2d8cff" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      <div className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold">Recent scans</h2>
          <Link to="/history" className="text-sm text-brand-400">View all</Link>
        </div>
        {data.recent.length === 0 ? (
          <p className="text-sm text-slate-400">Nothing yet.</p>
        ) : (
          <ul className="divide-y divide-white/10">
            {data.recent.map((s) => (
              <li key={s.id} className="space-y-2 py-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <Link to={`/history/${s.id}`} className="min-w-0 truncate text-sm hover:text-brand-400">{s.submitted_url}</Link>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500">{new Date(s.created_at).toLocaleString()}</span>
                    <span className="text-sm font-semibold">Risk {s.risk_score}/100</span>
                    <VerdictBadge verdict={s.verdict} />
                  </div>
                </div>
                {s.explanation && (
                  <p className="text-xs leading-relaxed text-slate-400">
                    <span className="font-semibold text-slate-300">Why: </span>
                    {s.explanation}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}