const styles = {
  SAFE: "bg-emerald-500/15 text-emerald-300 border-emerald-500/40",
  SUSPICIOUS: "bg-amber-500/15 text-amber-300 border-amber-500/40",
  PHISHING: "bg-red-500/15 text-red-300 border-red-500/40",
};

export default function VerdictBadge({ verdict }) {
  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${styles[verdict] || ""}`}>
      {verdict}
    </span>
  );
}
