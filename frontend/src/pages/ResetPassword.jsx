import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, errorMessage } from "../api.js";

export default function ResetPassword() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    setBusy(true);
    try {
      await api.post("/auth/reset-password", { email, code, new_password: password });
      navigate("/login?reset=1");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md card">
      <h1 className="mb-2 text-2xl font-bold">Reset password</h1>
      <p className="mb-4 text-sm text-slate-400">Enter the code sent to {email || "your email"} and choose a new password.</p>
      <form onSubmit={submit} className="space-y-3">
        <input className="input text-center text-xl tracking-widest" inputMode="numeric" maxLength={6} placeholder="123456" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} required />
        <input className="input" type="password" placeholder="New password (min 8 characters)" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="btn-primary w-full" disabled={busy || code.length !== 6}>{busy ? "Saving…" : "Reset password"}</button>
      </form>
      <p className="mt-4 text-sm"><Link to="/forgot-password" className="text-brand-400">Request a new code</Link></p>
    </div>
  );
}
