import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "../api.js";
import VerdictBadge from "../components/VerdictBadge.jsx";

export default function History() {
  const [scans, setScans] = useState(null);
  const [q, setQ] = useState("");
  const [verdict, setVerdict] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const params = {};
      if (q) params.q = q;
      if (verdict) params.verdict = verdict;
      const res = await api.get("/history", { params });
      setScans(res.data);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  useEffect(() => { load(); }, [verdict]); // eslint-disable-line react-hooks/exhaustive-deps

  async function remove(id) {
    if (!window.confirm("Delete this scan from your history?")) return;
    try {
      await api.delete(`/history/${id}`);
      setScans((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Scan history</h1>
      <form onSubmit={(e) => { e.preventDefault(); load(); }} className="card flex flex-col gap-3 md:flex-row">
        <input className="input" placeholder="Search URLs" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="input md:w-56" value={verdict} onChange={(e) => setVerdict(e.target.value)}>
          <option value="">All verdicts</option>
          <option value="SAFE">SAFE</option>
          <option value="SUSPICIOUS">SUSPICIOUS</option>
          <option value="PHISHING">PHISHING</option>
        </select>
        <button className="btn-ghost">Search</button>
      </form>
      {error && <p className="text-red-300">{error}</p>}
      {scans === null && !error && <p className="text-slate-400">Loading…</p>}
      {scans && scans.length === 0 && (
        <div className="card text-slate-300">No scans yet. <Link to="/scan" className="text-brand-400">Scan your first URL</Link>.</div>
      )}
      {scans && scans.length > 0 && (
        <div className="space-y-3">
          {scans.map((s) => (
            <div key={s.id} className="card flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div className="min-w-0">
                <p className="truncate text-sm">{s.submitted_url}</p>
                <p className="text-xs text-slate-500">{new Date(s.created_at).toLocaleString()} · score {s.risk_score}</p>
              </div>
              <div className="flex items-center gap-2">
                <VerdictBadge verdict={s.verdict} />
                <Link to={`/history/${s.id}`} className="btn-ghost px-3 py-1.5 text-sm">View</Link>
                <button onClick={() => remove(s.id)} className="btn-ghost px-3 py-1.5 text-sm text-red-300">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
