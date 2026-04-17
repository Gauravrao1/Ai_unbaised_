import { ArrowLeft, Download, RefreshCw } from 'lucide-react'
import Dashboard from './Dashboard'

export default function ResultsPage({ analysis, mitigation, explanation, onBack, onDownload, onReset }) {
  if (!analysis) {
    return null
  }

  return (
    <div className="space-y-8">
      <header className="glass-panel rounded-[2rem] p-6 lg:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-white sm:text-5xl">
              BiasLens AI dashboard
            </h1>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-700 bg-slate-950/60 px-5 py-3 font-semibold text-slate-100 transition hover:border-slate-500"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to upload
            </button>
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-2 rounded-2xl border border-emerald-400/30 bg-emerald-400/10 px-5 py-3 font-semibold text-emerald-100 transition hover:bg-emerald-400/20"
            >
              <RefreshCw className="h-4 w-4" />
              New analysis
            </button>
            <button
              type="button"
              onClick={onDownload}
              className="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              <Download className="h-4 w-4" />
              Download report
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <SummaryCard label="Fairness score" value={`${analysis.fairness_score?.toFixed?.(0) ?? analysis.fairness_score}%`} tone="accent" />
          <SummaryCard label="Bias risk" value={`${analysis.bias_risk_score?.toFixed?.(0) ?? analysis.bias_risk_score}/100`} tone="warning" />
          <SummaryCard label="Accuracy" value={`${(analysis.model_accuracy * 100).toFixed(1)}%`} tone="info" />
        </div>
      </header>

      <Dashboard analysis={analysis} mitigation={mitigation} explanation={explanation} />
    </div>
  )
}

function SummaryCard({ label, value, tone }) {
  const classes = {
    accent: 'from-emerald-400/20 to-cyan-400/10 border-emerald-400/20',
    warning: 'from-amber-400/20 to-orange-400/10 border-amber-400/20',
    info: 'from-sky-400/20 to-cyan-400/10 border-sky-400/20',
  }

  return (
    <div className={`rounded-3xl border bg-gradient-to-br p-5 ${classes[tone] || classes.accent}`}>
      <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{label}</div>
      <div className="mt-3 font-display text-3xl font-bold text-white">{value}</div>
    </div>
  )
}