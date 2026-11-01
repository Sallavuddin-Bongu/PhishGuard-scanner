import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, errorMessage } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Login() {
  const { saveSession } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      saveSession(res.data);
      navigate("/dashboard");
    } catch (err) {
      if (err.response?.status === 403) {
        navigate(`/verify?email=${encodeURIComponent(email)}`);
        return;
      }
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md card">
      <h1 className="mb-4 text-2xl font-bold">Log in</h1>
      {params.get("expired") && (
        <p className="mb-4 rounded-lg bg-amber-500/10 p-3 text-sm text-amber-300">Your session expired. Please log in again.</p>
      )}
      <form onSubmit={submit} className="space-y-3">
        <input className="input" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Logging in…" : "Log in"}</button>
      </form>
      <div className="mt-4 flex justify-between text-sm text-slate-400">
        <Link to="/forgot-password" className="text-brand-400">Forgot password?</Link>
        <Link to="/register" className="text-brand-400">Register</Link>
      </div>
    </div>
  );
}
