import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, FileUp, Sparkles } from 'lucide-react'
import ResultsPage from './pages/ResultsPage'
import { analyzeBias, explainBias, mitigateBias, uploadArtifacts } from './lib/api'

const sampleTargetHint = 'If your CSV already has a target column like selected, approved, or label, leave this blank.'

export default function App() {
  const [view, setView] = useState(() => (window.location.hash === '#results' ? 'results' : 'input'))
  const [csvFile, setCsvFile] = useState(null)
  const [modelFile, setModelFile] = useState(null)
  const [targetColumn, setTargetColumn] = useState('')
  const [analysisId, setAnalysisId] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [mitigation, setMitigation] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const canAnalyze = useMemo(() => Boolean(csvFile) && !loading, [csvFile, loading])

  useEffect(() => {
    const syncView = () => {
      setView(window.location.hash === '#results' ? 'results' : 'input')
    }

    window.addEventListener('hashchange', syncView)
    syncView()

    return () => window.removeEventListener('hashchange', syncView)
  }, [])

  async function handleAnalyze() {
    if (!csvFile) {
      setError('Upload a CSV dataset first.')
      return
    }

    setLoading(true)
    setError('')
    setMitigation(null)
    try {
      const uploadResponse = await uploadArtifacts(csvFile, modelFile, targetColumn.trim() || undefined)
      setAnalysisId(uploadResponse.analysis_id)
      const analysisResponse = await analyzeBias({
        analysis_id: uploadResponse.analysis_id,
        target_column: targetColumn.trim() || uploadResponse.detected_target_column,
      })
      setAnalysis(analysisResponse)
      const explanationResponse = await explainBias({
        analysis_id: uploadResponse.analysis_id,
        bias_report: analysisResponse,
      })
      setExplanation(explanationResponse)
      window.history.pushState(null, '', '#results')
      setView('results')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (requestError) {
      setError(requestError.message || 'Unable to analyze bias.')
    } finally {
      setLoading(false)
    }
  }

  async function handleMitigate() {
    if (!analysisId) {
      return
    }

    setLoading(true)
    setError('')
    try {
      const mitigationResponse = await mitigateBias({
        analysis_id: analysisId,
        target_column: targetColumn.trim() || analysis?.target_column,
        sensitive_column: analysis?.sensitive_column,
        strategy: 'reweighing',
      })
      setMitigation(mitigationResponse)
      const explanationResponse = await explainBias({
        analysis_id: analysisId,
        bias_report: mitigationResponse.after,
      })
      setExplanation(explanationResponse)
    } catch (requestError) {
      setError(requestError.message || 'Unable to mitigate bias.')
    } finally {
      setLoading(false)
    }
  }

  function openInputView() {
    window.history.pushState(null, '', '#upload')
    setView('input')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function downloadReport() {
    if (!analysis) {
      return
    }

    const payload = {
      analysis,
      mitigation,
      explanation,
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `biaslens-report-${analysisId || 'report'}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="relative min-h-screen overflow-hidden text-slate-100">
      <div className="absolute inset-0 grid-fade opacity-45" />
      <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="glass-panel rounded-[2rem] p-6 lg:p-8">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/25 bg-cyan-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">
                <Sparkles className="h-4 w-4" />
                UN SDG 10 fairness intelligence
              </div>
              <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-white sm:text-6xl">
                BiasLens AI
              </h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300 sm:text-lg">
                A startup-style fairness dashboard that detects bias in datasets and ML models, explains it in plain language,
                and suggests mitigations that reduce inequality across gender, caste, age, and income groups.
              </p>
            </div>
            <div className="grid gap-3 sm:min-w-[320px]">
              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/50 p-4">
                <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Current mode</div>
                <div className="mt-2 text-lg font-semibold text-white">
                  {view === 'results' ? 'Results page with expandable visualizations' : 'Bias analysis + AI explanation + mitigation'}
                </div>
              </div>
              <div className="rounded-2xl border border-slate-700/70 bg-slate-950/50 p-4 text-sm text-slate-300">
                Frontend: React + Tailwind + Recharts. Backend: FastAPI + Fairlearn + AIF360 + Gemini.
              </div>
            </div>
          </div>
        </header>

        {view === 'input' ? (
          <main className="mt-8 grid gap-8 xl:grid-cols-[0.92fr_1.08fr]">
            <section className="glass-panel rounded-[2rem] p-6 lg:p-8">
              <div className="mb-6">
                <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Data input</div>
                <h2 className="mt-2 font-display text-2xl font-semibold text-white">Upload CSV or trained model</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  The app auto-detects likely sensitive attributes, runs fairness analysis, and generates human-friendly insights.
                </p>
              </div>

              <div className="space-y-4">
                <label className="block rounded-3xl border border-dashed border-cyan-400/30 bg-slate-950/30 p-5 transition hover:border-cyan-300/60">
                  <div className="flex items-center gap-3 text-cyan-200">
                    <FileUp className="h-5 w-5" />
                    <span className="font-semibold">CSV dataset</span>
                  </div>
                  <input
                    className="mt-4 block w-full cursor-pointer rounded-xl border border-slate-700 bg-slate-900/70 text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:font-semibold file:text-slate-950"
                    type="file"
                    accept=".csv"
                    onChange={(event) => setCsvFile(event.target.files?.[0] || null)}
                  />
                </label>

                <label className="block rounded-3xl border border-dashed border-slate-700/70 bg-slate-950/30 p-5 transition hover:border-slate-500/80">
                  <div className="flex items-center gap-3 text-slate-200">
                    <span className="font-semibold">Optional trained model</span>
                  </div>
                  <input
                    className="mt-4 block w-full cursor-pointer rounded-xl border border-slate-700 bg-slate-900/70 text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-400 file:px-4 file:py-2 file:font-semibold file:text-slate-950"
                    type="file"
                    accept=".pkl,.joblib"
                    onChange={(event) => setModelFile(event.target.files?.[0] || null)}
                  />
                </label>

                <div>
                  <label className="text-sm font-medium text-slate-200">Target column</label>
                  <input
                    className="mt-2 w-full rounded-2xl border-slate-700 bg-slate-950/60 text-slate-100 placeholder:text-slate-500 focus:border-cyan-400 focus:ring-cyan-400"
                    placeholder="selected"
                    value={targetColumn}
                    onChange={(event) => setTargetColumn(event.target.value)}
                  />
                  <p className="mt-2 text-xs leading-5 text-slate-400">{sampleTargetHint}</p>
                </div>

                <div className="flex flex-wrap gap-3 pt-2">
                  <button
                    type="button"
                    onClick={handleAnalyze}
                    disabled={!canAnalyze}
                    className="inline-flex items-center gap-2 rounded-2xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {loading ? 'Processing...' : 'Analyze bias'}
                    <ArrowRight className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    onClick={handleMitigate}
                    disabled={!analysis || loading}
                    className="inline-flex items-center gap-2 rounded-2xl border border-emerald-400/30 bg-emerald-400/10 px-5 py-3 font-semibold text-emerald-100 transition hover:bg-emerald-400/20 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Try mitigation
                  </button>
                </div>

                {error ? <div className="rounded-2xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-100">{error}</div> : null}
              </div>
            </section>

            <section className="glass-panel rounded-[2rem] p-6 lg:p-8">
              <div className="mb-6">
                <div className="text-xs uppercase tracking-[0.24em] text-slate-400">What you get</div>
                <h2 className="mt-2 font-display text-2xl font-semibold text-white">A separate result page after analysis</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  After you run the analysis, the app switches into a dedicated dashboard view with expandable visual cards.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <InfoTile
                  title="Seamless page switch"
                  text="Results move into a dedicated view without a hard reload, so the experience feels like a real app."
                />
                <InfoTile
                  title="Expand and collapse"
                  text="Every chart and key visualization can be minimized or maximized to fit your screen."
                />
                <InfoTile
                  title="Downloadable report"
                  text="Export the analysis, mitigation, and explanation as JSON for sharing or follow-up."
                />
                <InfoTile
                  title="Indian fairness context"
                  text="The dashboard keeps the SDG 10 narrative visible with caste and gender impact framing."
                />
              </div>
            </section>
          </main>
        ) : (
          <main className="mt-8">
            <ResultsPage
              analysis={analysis}
              mitigation={mitigation}
              explanation={explanation}
              onBack={openInputView}
              onReset={() => {
                setAnalysis(null)
                setMitigation(null)
                setExplanation(null)
                setAnalysisId('')
                setCsvFile(null)
                setModelFile(null)
                setTargetColumn('')
                openInputView()
              }}
              onDownload={downloadReport}
            />
          </main>
        )}
      </div>
    </div>
  )
}

function InfoTile({ title, text }) {
  return (
    <div className="rounded-3xl border border-slate-700/70 bg-slate-950/40 p-5">
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-6 text-slate-300">{text}</div>
    </div>
  )
}
