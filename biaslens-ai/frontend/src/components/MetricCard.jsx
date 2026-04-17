export default function MetricCard({ label, value, hint, accent = 'accent' }) {
  const classes = {
    accent: 'from-emerald-400/20 to-cyan-400/10 border-emerald-400/20',
    warning: 'from-amber-400/20 to-orange-400/10 border-amber-400/20',
    danger: 'from-red-400/20 to-rose-400/10 border-red-400/20',
    info: 'from-sky-400/20 to-cyan-400/10 border-sky-400/20',
  }

  return (
    <div className={`glass-panel rounded-3xl border bg-gradient-to-br p-5 ${classes[accent] || classes.accent}`}>
      <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{label}</div>
      <div className="mt-3 font-display text-3xl font-bold text-white">{value}</div>
      <div className="mt-2 text-sm leading-6 text-slate-300">{hint}</div>
    </div>
  )
}
