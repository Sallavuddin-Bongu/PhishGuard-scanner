import { useEffect, useState } from "react";
import { api, errorMessage } from "../api.js";

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/admin/stats"), api.get("/admin/users")])
      .then(([s, u]) => {
        setStats(s.data);
        setUsers(u.data);
      })
      .catch((e) => setError(errorMessage(e)));
  }, []);

  if (error) return <div className="card text-red-300">{error}</div>;
  if (!stats) return <p className="text-slate-400">Loading…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin dashboard</h1>
      <div className="grid gap-4 md:grid-cols-5">
        <div className="card"><p className="text-sm text-slate-400">Users</p><p className="text-3xl font-bold">{stats.total_users}</p></div>
        <div className="card"><p className="text-sm text-slate-400">Total scans</p><p className="text-3xl font-bold">{stats.total_scans}</p></div>
        <div className="card"><p className="text-sm text-slate-400">Safe</p><p className="text-3xl font-bold text-emerald-300">{stats.counts.SAFE}</p></div>
        <div className="card"><p className="text-sm text-slate-400">Suspicious</p><p className="text-3xl font-bold text-amber-300">{stats.counts.SUSPICIOUS}</p></div>
        <div className="card"><p className="text-sm text-slate-400">Phishing</p><p className="text-3xl font-bold text-red-300">{stats.counts.PHISHING}</p></div>
      </div>
      <div className="card overflow-x-auto">
        <h2 className="mb-3 font-semibold">Users</h2>
        <table className="w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr><th className="py-2">Email</th><th>Role</th><th>Scans</th><th>Joined</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-white/10">
                <td className="py-2">{u.email}</td>
                <td>{u.role}</td>
                <td>{u.scan_count}</td>
                <td>{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
