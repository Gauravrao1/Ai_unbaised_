import { Maximize2, Minimize2 } from 'lucide-react'
import { useState } from 'react'

export default function CollapsiblePanel({
  eyebrow,
  title,
  description,
  defaultExpanded = true,
  collapsedHint,
  actions = null,
  allowMaximize = true,
  bodyClassName = 'mt-5',
  maximizedBodyClassName = 'mt-5',
  children,
}) {
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [maximized, setMaximized] = useState(false)

  const shellClasses = maximized
    ? 'fixed inset-4 z-50 overflow-y-auto rounded-[2rem] border border-slate-700/80 bg-slate-950/96 p-5 shadow-2xl shadow-black/60 backdrop-blur-xl md:inset-6'
    : 'glass-panel rounded-[2rem] p-5'

  return (
    <>
      {maximized ? (
        <button
          type="button"
          aria-label="Close maximized panel"
          onClick={() => setMaximized(false)}
          className="fixed inset-0 z-40 cursor-default bg-slate-950/70"
        />
      ) : null}
      <section className={shellClasses}>
        <div className="flex items-start justify-between gap-4">
          <div>
            {eyebrow ? <div className="text-xs uppercase tracking-[0.24em] text-slate-400">{eyebrow}</div> : null}
            <h3 className="mt-2 text-xl font-display font-semibold text-white">{title}</h3>
            {description ? <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p> : null}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            {allowMaximize ? (
              <button
                type="button"
                onClick={() => setMaximized((current) => !current)}
                className="inline-flex items-center gap-2 rounded-full border border-slate-700/80 bg-slate-950/60 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200 transition hover:border-slate-500 hover:bg-slate-900/80"
                aria-expanded={maximized}
                aria-label={maximized ? 'Minimize chart' : 'Maximize chart'}
              >
                {maximized ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
                {maximized ? 'Minimize' : 'Maximize'}
              </button>
            ) : null}
            <button
              type="button"
              onClick={() => setExpanded((current) => !current)}
              className="inline-flex items-center gap-2 rounded-full border border-slate-700/80 bg-slate-950/60 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200 transition hover:border-slate-500 hover:bg-slate-900/80"
              aria-expanded={expanded}
              aria-label={expanded ? 'Collapse panel' : 'Expand panel'}
            >
              {expanded ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
              {expanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
        </div>

      {expanded ? (
        <div className={maximized ? maximizedBodyClassName : bodyClassName}>{children}</div>
      ) : collapsedHint ? (
        <div className="mt-4 rounded-2xl border border-slate-700/70 bg-slate-950/40 px-4 py-3 text-sm text-slate-300">
          {collapsedHint}
        </div>
      ) : null}
      </section>
    </>
  )
}