import { useState } from "react";
import { Link } from "react-router-dom";
import { api, errorMessage } from "../api.js";
import VerdictBadge from "../components/VerdictBadge.jsx";

const MAX_BULK = 25;

const externalText = {
  flagged: "Google Safe Browsing flagged this URL.",
  clear: "Google Safe Browsing did not flag this URL.",
  unavailable: "Google Safe Browsing was unavailable. This does not mean the URL is safe.",
  not_configured: "Google Safe Browsing is not configured on this server.",
};

const featureLabels = {
  url_length: "Total URL length (characters)",
  domain_length: "Domain length (characters)",
  is_ip_host: "Uses an IP address instead of a domain name (1 = yes)",
  tld_length: "Top-level domain length",
  num_subdomains: "Number of subdomains",
  num_letters: "Number of letters",
  letter_ratio: "Share of letters in the URL",
  num_digits: "Number of digits",
  digit_ratio: "Share of digits in the URL",
  num_special: "Number of special characters",
  special_ratio: "Share of special characters",
  num_equals: "Number of '=' signs",
  num_question_marks: "Number of '?' characters",
  num_ampersands: "Number of '&' characters",
  num_percent_encoded: "Number of percent-encoded characters",
  percent_encoded_ratio: "Share of percent-encoded characters",
  num_hyphens_in_domain: "Hyphens in the domain",
  num_dots: "Number of dots",
  path_depth: "Path depth (number of / segments)",
  is_https: "Uses HTTPS (1 = yes)",
};

function formatValue(value) {
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(3);
  return String(value);
}

function Reasons({ checks }) {
  if (!checks || checks.length === 0) {
    return <span className="text-sm text-slate-400">None of the rule checks were triggered.</span>;
  }
  return (
    <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
      {checks.map((c, i) => <li key={i}>{c.reason}</li>)}
    </ul>
  );
}

export default function Scan() {
  // Single URL
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // Bulk
  const [bulkText, setBulkText] = useState("");
  const [bulkRows, setBulkRows] = useState([]);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [bulkProgress, setBulkProgress] = useState("");
  const [bulkNotice, setBulkNotice] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setBusy(true);
    try {
      const res = await api.post("/scan", { url });
      setResult(res.data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function runBulk(e) {
    e.preventDefault();
    const lines = bulkText.split("\n").map((l) => l.trim()).filter(Boolean);
    if (lines.length === 0) return;
    setBulkNotice("");
    if (lines.length > MAX_BULK) {
      setBulkNotice(`Only the first ${MAX_BULK} URLs will be scanned. You entered ${lines.length}.`);
    }
    const urls = lines.slice(0, MAX_BULK);
    setBulkRows([]);
    setBulkBusy(true);
    const rows = [];
    for (let i = 0; i < urls.length; i++) {
      setBulkProgress(`Scanning ${i + 1} of ${urls.length}…`);
      try {
        const res = await api.post("/scan", { url: urls[i] });
        rows.push({ url: urls[i], data: res.data });
      } catch (err) {
        rows.push({ url: urls[i], error: errorMessage(err) });
      }
    }
    setBulkRows(rows);
    setBulkProgress("");
    setBulkBusy(false);
  }

  const checks = result?.triggered_checks ?? [];
  const features = result?.features ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Scan a URL</h1>
        <p className="text-sm text-slate-400">Enter an http or https address. Every scan is saved to your history.</p>
      </div>

      <form onSubmit={submit} className="card flex flex-col gap-3 md:flex-row">
        <input className="input" placeholder="https://example.com" value={url} onChange={(e) => setUrl(e.target.value)} required />
        <button className="btn-primary md:w-40" disabled={busy}>{busy ? "Scanning…" : "Scan"}</button>
      </form>
      {error && <div className="card border-red-500/40 text-red-300">{error}</div>}

      {result && (
        <div className="card space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <VerdictBadge verdict={result.verdict} />
            <span className="text-sm text-slate-400">Risk score {result.risk_score} / 100</span>
          </div>
          <p className="break-all text-sm"><span className="text-slate-400">URL: </span>{result.submitted_url}</p>
          <p className="text-sm"><span className="text-slate-400">ML phishing probability: </span>{(result.ml_probability * 100).toFixed(1)}%</p>
          <p className="text-sm"><span className="text-slate-400">Rule checks score: </span>{result.heuristic_score} / 100</p>
          <p className="text-sm"><span className="text-slate-400">External check: </span>{externalText[result.external_status]}</p>

          <div>
            <h2 className="mb-2 font-semibold">Why this verdict</h2>
            <p className="whitespace-pre-line text-sm text-slate-300">{result.explanation}</p>
          </div>

          <div>
            <h3 className="mb-2 font-semibold">Warning signs found by rule checks</h3>
            <Reasons checks={checks} />
          </div>

          <div>
            <h3 className="mb-2 font-semibold">URL features the model used</h3>
            <p className="mb-2 text-xs text-slate-500">
              The model combines all of these values together. No single value decides the result on its own.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-slate-400">
                  <tr>
                    <th className="py-1 pr-4 font-normal">Feature</th>
                    <th className="py-1 font-normal">Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {Object.entries(features).map(([key, value]) => (
                    <tr key={key}>
                      <td className="py-1 pr-4 text-slate-300">{featureLabels[key] ?? key}</td>
                      <td className="py-1 font-mono text-slate-200">{formatValue(value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <p className="text-xs text-slate-500">{result.safety_note}</p>
          <Link to={`/history/${result.id}`} className="btn-ghost">View full details</Link>
        </div>
      )}

      <div className="card space-y-4">
        <div>
          <h2 className="text-xl font-bold">Bulk scan</h2>
          <p className="text-sm text-slate-400">Paste up to {MAX_BULK} URLs, one per line. Each one is scanned and saved.</p>
        </div>
        <form onSubmit={runBulk} className="space-y-3">
          <textarea
            className="input min-h-[140px] w-full font-mono text-sm"
            placeholder={"https://github.com\nhttp://sbi.update-account.xyz/login"}
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
          />
          <div className="flex flex-wrap items-center gap-3">
            <button className="btn-primary" disabled={bulkBusy}>
              {bulkBusy ? "Scanning…" : "Scan URLs"}
            </button>
            {bulkProgress && <span className="text-sm text-slate-400">{bulkProgress}</span>}
          </div>
          {bulkNotice && <p className="text-sm text-amber-300">{bulkNotice}</p>}
        </form>

        {bulkRows.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-slate-400">
                <tr>
                  <th className="py-2 pr-4 font-normal">URL</th>
                  <th className="py-2 pr-4 font-normal">Score</th>
                  <th className="py-2 pr-4 font-normal">Verdict</th>
                  <th className="py-2 font-normal">Why</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10 align-top">
                {bulkRows.map((row, i) => (
                  <tr key={i}>
                    <td className="break-all py-2 pr-4">{row.url}</td>
                    {row.data ? (
                      <>
                        <td className="py-2 pr-4 font-semibold">{row.data.risk_score}</td>
                        <td className="py-2 pr-4"><VerdictBadge verdict={row.data.verdict} /></td>
                        <td className="py-2">
                          <p className="mb-2 whitespace-pre-line text-xs text-slate-400">{row.data.explanation}</p>
                          <Reasons checks={row.data.triggered_checks} />
                        </td>
                      </>
                    ) : (
                      <td colSpan={3} className="py-2 text-red-300">{row.error}</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}