import CollapsiblePanel from './CollapsiblePanel'
const formatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 })

export default function ComparisonTable({ before = null, after = null, delta = null }) {
  if (!before) {
    return null
  }

  const rows = [
    ['Model accuracy', before.model_accuracy, after?.model_accuracy],
    ['Fairness score', before.fairness_score, after?.fairness_score],
    ['Bias risk score', before.bias_risk_score, after?.bias_risk_score],
    ['Demographic parity difference', before.metrics?.demographic_parity_difference, after?.metrics?.demographic_parity_difference],
    ['Equal opportunity difference', before.metrics?.equal_opportunity_difference, after?.metrics?.equal_opportunity_difference],
    ['Disparate impact', before.metrics?.disparate_impact, after?.metrics?.disparate_impact],
  ]

  return (
    <CollapsiblePanel
      eyebrow="Before and after"
      title="Mitigation comparison"
      collapsedHint="Expand to compare before and after metrics."
    >
      <div className="overflow-hidden rounded-2xl border border-slate-700/70">
        <table className="min-w-full divide-y divide-slate-700/70 text-left text-sm">
          <thead className="bg-slate-950/40 text-slate-300">
            <tr>
              <th className="px-4 py-3 font-medium">Metric</th>
              <th className="px-4 py-3 font-medium">Before</th>
              <th className="px-4 py-3 font-medium">After</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 bg-slate-950/20 text-slate-100">
            {rows.map(([label, beforeValue, afterValue]) => (
              <tr key={label}>
                <td className="px-4 py-3 text-slate-300">{label}</td>
                <td className="px-4 py-3">{formatValue(beforeValue)}</td>
                <td className="px-4 py-3">{formatValue(afterValue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {delta ? (
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {Object.entries(delta).map(([key, value]) => (
            <div key={key} className="rounded-2xl border border-slate-700/70 bg-slate-950/40 p-4 text-sm text-slate-200">
              <div className="text-slate-400">{key.replaceAll('_', ' ')}</div>
              <div className="mt-2 text-xl font-semibold text-white">{formatter.format(value)}</div>
            </div>
          ))}
        </div>
      ) : null}
    </CollapsiblePanel>
  )
}

function formatValue(value) {
  if (value === null || value === undefined) {
    return '—'
  }
  if (typeof value === 'number') {
    return formatter.format(value)
  }
  return String(value)
}
