import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import CollapsiblePanel from './CollapsiblePanel'

const metricColors = ['#38bdf8', '#23ad78', '#f59e0b', '#ef4444']

export default function BiasChart({ groupMetrics = {}, beforeMetrics = {}, afterMetrics = null }) {
  const groupData = Object.entries(groupMetrics).map(([group, metrics]) => ({
    group,
    selectionRate: Number(metrics.selection_rate || 0) * 100,
    tpr: Number(metrics.true_positive_rate || 0) * 100,
  }))

  const fairnessData = [
    {
      name: 'DP diff',
      before: Math.abs(Number(beforeMetrics.demographic_parity_difference || 0)) * 100,
      after: afterMetrics ? Math.abs(Number(afterMetrics.demographic_parity_difference || 0)) * 100 : null,
    },
    {
      name: 'EO diff',
      before: Math.abs(Number(beforeMetrics.equal_opportunity_difference || 0)) * 100,
      after: afterMetrics ? Math.abs(Number(afterMetrics.equal_opportunity_difference || 0)) * 100 : null,
    },
    {
      name: 'SPD',
      before: Math.abs(Number(beforeMetrics.statistical_parity_difference || 0)) * 100,
      after: afterMetrics ? Math.abs(Number(afterMetrics.statistical_parity_difference || 0)) * 100 : null,
    },
    {
      name: 'DI gap',
      before: Math.abs(1 - Number(beforeMetrics.disparate_impact || 1)) * 100,
      after: afterMetrics ? Math.abs(1 - Number(afterMetrics.disparate_impact || 1)) * 100 : null,
    },
  ]

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <CollapsiblePanel
        eyebrow="Protected group comparison"
        title="Selection rate by group"
        collapsedHint="Expand to view."
        bodyClassName="mt-4 h-80 w-full"
        maximizedBodyClassName="mt-4 h-[72vh] w-full"
      >
        <div className="h-full w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={groupData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.14)" />
              <XAxis dataKey="group" tick={{ fill: '#cbd5e1', fontSize: 12 }} />
              <YAxis tick={{ fill: '#cbd5e1', fontSize: 12 }} unit="%" />
              <Tooltip
                contentStyle={{
                  background: 'rgba(2, 6, 23, 0.96)',
                  border: '1px solid rgba(148, 163, 184, 0.2)',
                  borderRadius: '16px',
                  color: '#fff',
                }}
              />
              <Legend />
              <Bar dataKey="selectionRate" name="Selection rate" radius={[12, 12, 0, 0]}>
                {groupData.map((entry, index) => (
                  <Cell key={`selection-${entry.group}`} fill={metricColors[index % metricColors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CollapsiblePanel>

      <CollapsiblePanel
        eyebrow="Model performance vs fairness"
        title="Fairness metric gap"
        collapsedHint="Expand to view."
        bodyClassName="mt-4 h-80 w-full"
        maximizedBodyClassName="mt-4 h-[72vh] w-full"
      >
        <div className="h-full w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={fairnessData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.14)" />
              <XAxis dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 12 }} />
              <YAxis tick={{ fill: '#cbd5e1', fontSize: 12 }} unit="%" />
              <Tooltip
                contentStyle={{
                  background: 'rgba(2, 6, 23, 0.96)',
                  border: '1px solid rgba(148, 163, 184, 0.2)',
                  borderRadius: '16px',
                  color: '#fff',
                }}
              />
              <Legend />
              <Bar dataKey="before" name="Before mitigation" fill="#ef4444" radius={[12, 12, 0, 0]} />
              {afterMetrics ? <Bar dataKey="after" name="After mitigation" fill="#23ad78" radius={[12, 12, 0, 0]} /> : null}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CollapsiblePanel>
    </div>
  )
}
