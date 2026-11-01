import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, errorMessage } from "../api.js";
import VerdictBadge from "../components/VerdictBadge.jsx";

export default function ScanDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [scan, setScan] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get(`/history/${id}`).then((r) => setScan(r.data)).catch((e) => setError(errorMessage(e)));
  }, [id]);

  async function remove() {
    if (!window.confirm("Delete this scan?")) return;
    try {
      await api.delete(`/history/${id}`);
      navigate("/history");
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  if (error) return <div className="card text-red-300">{error} <Link to="/history" className="text-brand-400">Back to history</Link></div>;
  if (!scan) return <p className="text-slate-400">Loading…</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Scan details</h1>
        <VerdictBadge verdict={scan.verdict} />
      </div>
      <div className="card space-y-3 text-sm">
        <p className="break-all"><span className="text-slate-400">Submitted: </span>{scan.submitted_url}</p>
        <p className="break-all"><span className="text-slate-400">Normalized: </span>{scan.normalized_url}</p>
        <p><span className="text-slate-400">Scanned: </span>{new Date(scan.created_at).toLocaleString()}</p>
        <p><span className="text-slate-400">Risk score: </span>{scan.risk_score} / 100 (80% model, 20% rules)</p>
        <p><span className="text-slate-400">ML phishing probability: </span>{(scan.ml_probability * 100).toFixed(1)}%</p>
        <p><span className="text-slate-400">Detection method: </span>{scan.detection_method}</p>
        <p className="text-slate-300">{scan.explanation}</p>
      </div>
      <div className="card">
        <h2 className="mb-3 font-semibold">Rule checks triggered</h2>
        {scan.triggered_checks.length === 0 ? (
          <p className="text-sm text-slate-400">None.</p>
        ) : (
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
            {scan.triggered_checks.map((c) => <li key={c.name}>{c.reason}</li>)}
          </ul>
        )}
      </div>
      <div className="card">
        <h2 className="mb-3 font-semibold">URL features used by the model</h2>
        <div className="grid grid-cols-2 gap-2 text-xs md:grid-cols-4">
          {Object.entries(scan.features).map(([k, v]) => (
            <div key={k} className="rounded bg-navy-950 p-2"><span className="text-slate-400">{k}</span><div>{Number(v).toFixed(3).replace(/\.?0+$/, "")}</div></div>
          ))}
        </div>
      </div>
      <p className="text-xs text-slate-500">{scan.safety_note}</p>
      <div className="flex gap-3">
        <Link to="/history" className="btn-ghost">Back</Link>
        <button onClick={remove} className="btn-ghost text-red-300">Delete scan</button>
      </div>
    </div>
  );
}
