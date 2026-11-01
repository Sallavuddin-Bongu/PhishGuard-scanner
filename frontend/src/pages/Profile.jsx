import { useState } from "react";
import { api, errorMessage } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Profile() {
  const { user } = useAuth();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setBusy(true);
    try {
      await api.put("/profile", { current_password: current, new_password: next });
      setMessage("Password changed.");
      setCurrent("");
      setNext("");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-6">
      <h1 className="text-2xl font-bold">Profile</h1>
      <div className="card text-sm">
        <p><span className="text-slate-400">Email: </span>{user.email}</p>
        <p><span className="text-slate-400">Role: </span>{user.role}</p>
        <p><span className="text-slate-400">Member since: </span>{new Date(user.created_at).toLocaleDateString()}</p>
      </div>
      <form onSubmit={submit} className="card space-y-3">
        <h2 className="font-semibold">Change password</h2>
        <input className="input" type="password" placeholder="Current password" value={current} onChange={(e) => setCurrent(e.target.value)} required />
        <input className="input" type="password" placeholder="New password (min 8 characters)" value={next} onChange={(e) => setNext(e.target.value)} required />
        {message && <p className="text-sm text-emerald-300">{message}</p>}
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Saving…" : "Change password"}</button>
      </form>
    </div>
  );
}
