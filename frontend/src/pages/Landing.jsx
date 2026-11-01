import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="space-y-10">
      <section className="py-10 text-center">
        <h1 className="text-4xl font-bold md:text-5xl">
          Check a link before you <span className="text-brand-400">click</span>.
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-slate-300">
          PhishGuard uses a machine learning model trained on phishing URLs, plus rule-based checks, to estimate
          whether a web address looks like a phishing attempt.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link to="/register" className="btn-primary">Create account</Link>
          <Link to="/login" className="btn-ghost">Log in</Link>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        <div className="card"><h3 className="font-semibold">Model + rules</h3><p className="mt-2 text-sm text-slate-300">A calibrated model score is combined with separate rule checks. Each is shown on its own.</p></div>
        <div className="card"><h3 className="font-semibold">Plain explanations</h3><p className="mt-2 text-sm text-slate-300">Every verdict lists the warning signs it found and what they mean.</p></div>
        <div className="card"><h3 className="font-semibold">Your history stays yours</h3><p className="mt-2 text-sm text-slate-300">You can only see and delete your own scans.</p></div>
      </section>
      <p className="text-center text-sm text-slate-400">
        Automated detection is not a guarantee. A SAFE result does not prove a site is safe.
      </p>
    </div>
  );
}
