import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, errorMessage } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Verify() {
  const { saveSession } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await api.post("/auth/verify-otp", { email, code });
      saveSession(res.data);
      navigate("/dashboard");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function resend() {
    setError("");
    setInfo("");
    try {
      await api.post("/auth/resend-otp", { email });
      setInfo("If this account needs verification, a new code has been sent.");
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div className="mx-auto max-w-md card">
      <h1 className="mb-2 text-2xl font-bold">Verify your email</h1>
      <p className="mb-4 text-sm text-slate-400">Enter the 6-digit code sent to {email || "your email"}.</p>
      <form onSubmit={submit} className="space-y-3">
        <input className="input text-center text-xl tracking-widest" inputMode="numeric" maxLength={6} placeholder="123456" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} required />
        {info && <p className="text-sm text-emerald-300">{info}</p>}
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="btn-primary w-full" disabled={busy || code.length !== 6}>{busy ? "Checking…" : "Verify"}</button>
      </form>
      <div className="mt-4 flex justify-between text-sm">
        <button onClick={resend} className="text-brand-400">Send a new code</button>
        <Link to="/login" className="text-slate-400">Back to login</Link>
      </div>
    </div>
  );
}
