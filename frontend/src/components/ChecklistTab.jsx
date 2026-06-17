import { useState, useEffect } from 'react'

export default function ChecklistTab({ pendingChecklist, onChecklistConsumed }) {
  const [goal, setGoal] = useState('')
  const [nationality, setNationality] = useState('')
  const [currentStatus, setCurrentStatus] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)


  useEffect(() => {
    if (!pendingChecklist) return

    const { goal: g, nationality: n, currentVisa: v } = pendingChecklist

    setGoal(g)
    setNationality(n || '')
    setCurrentStatus(v || '')
    setResult(null)
    setError(null)

    onChecklistConsumed()
    autoGenerate(g, n || '', v || '')
  }, [pendingChecklist?.goal])

  const autoGenerate = async (goalVal, nationalityVal, statusVal) => {
    if (!goalVal.trim()) return
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/checklist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: goalVal,
          nationality: nationalityVal || 'Extract from goal if mentioned',
          current_status: statusVal || 'Extract from goal if mentioned',
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch {
      setError('Could not connect to the server.')
    } finally {
      setIsLoading(false)
    }
  }

  const generateChecklist = async () => {
    if (!goal.trim() || !nationality.trim() || !currentStatus.trim()) return
    await autoGenerate(goal, nationality, currentStatus)
  }

  return (
    <div className="flex h-full" style={{ height: 'calc(100vh - 56px)' }}>

      {/* Left form */}
      <div className="w-80 border-r border-border bg-surface flex flex-col flex-shrink-0">
        <div className="p-6 flex-1 overflow-y-auto">
          <h2 className="text-base font-semibold text-text-primary mb-1">
            Generate your checklist
          </h2>
          <p className="text-sm text-text-secondary mb-6 leading-relaxed">
            Tell us your situation and we'll create a personalised step-by-step immigration plan.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-1.5">
                Your goal
              </label>
              <textarea
                value={goal}
                onChange={e => setGoal(e.target.value)}
                placeholder="e.g. Apply for Critical Skills Employment Permit"
                rows={3}
                className="w-full px-3 py-2.5 rounded-xl border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary text-sm transition-colors resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-1.5">
                Nationality
              </label>
              <input
                type="text"
                value={nationality}
                onChange={e => setNationality(e.target.value)}
                placeholder="e.g. Indian, Brazilian"
                className="w-full px-3 py-2.5 rounded-xl border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary text-sm transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-1.5">
                Current status in Ireland
              </label>
              <input
                type="text"
                value={currentStatus}
                onChange={e => setCurrentStatus(e.target.value)}
                placeholder="e.g. Student Stamp 2, Not in Ireland yet"
                className="w-full px-3 py-2.5 rounded-xl border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary text-sm transition-colors"
              />
            </div>

            <button
              onClick={generateChecklist}
              disabled={!goal.trim() || !nationality.trim() || !currentStatus.trim() || isLoading}
              className="w-full bg-primary text-background rounded-xl py-3 text-sm font-semibold hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors mt-2"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
                  Generating...
                </span>
              ) : (
                'Generate my checklist →'
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-700/50 rounded-xl text-sm text-red-400">
              {error}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border">
          <p className="text-xs text-text-secondary leading-relaxed">
            For guidance only. Always verify with official Irish government sources.
          </p>
        </div>
      </div>

      {/* Right results */}
      <div className="flex-1 overflow-y-auto chat-scrollbar p-6">
        {!result && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-5xl mb-4">✅</div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              Your plan will appear here
            </h3>
            <p className="text-text-secondary max-w-sm">
              Fill in your goal and situation on the left to generate a personalised checklist.
            </p>
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-text-secondary text-sm">
              Searching official sources and building your plan...
            </p>
          </div>
        )}

        {result && (
          <div className="max-w-3xl fade-in">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-text-primary">
                  Your personalised plan
                </h3>
                <p className="text-sm text-text-secondary mt-0.5">
                  {result.goal} · {result.nationality} · {result.current_status}
                </p>
              </div>
              <span className="text-sm bg-primary-light text-primary px-3 py-1 rounded-full font-medium">
                {result.steps.length} steps
              </span>
            </div>

            <div className="space-y-4">
              {result.steps.map((step, i) => {
                return (
                  <div key={i} className="bg-surface rounded-2xl border border-border p-5">
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 rounded-full bg-primary text-background text-sm font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                        {step.step_number}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-text-primary mb-1.5">
                          {step.title}
                        </h4>
                        <p className="text-sm text-text-secondary leading-relaxed">
                          {step.description}
                        </p>

                        {step.documents_required && step.documents_required.length > 0 && (
                          <div className="mt-3">
                            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
                              Documents required
                            </p>
                            <div className="flex flex-wrap gap-1.5">
                              {step.documents_required.map((doc, j) => {
                                return (
                                  <span
                                    key={j}
                                    className="text-xs bg-surface-2 border border-border px-2.5 py-1 rounded-full text-text-secondary"
                                  >
                                    {doc}
                                  </span>
                                )
                              })}
                            </div>
                          </div>
                        )}

                        <div className="flex flex-wrap items-center gap-4 mt-3">
                          {step.fee && (
                            <span className="text-xs font-medium text-accent">
                              💰 {step.fee}
                            </span>
                          )}
                          {step.estimated_time && (
                            <span className="text-xs text-text-secondary">
                              ⏱ {step.estimated_time}
                            </span>
                          )}
                          {step.official_link && (
                            <a
                              href={step.official_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-primary hover:underline"
                            >
                              Official link ↗
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {result.important_notes && result.important_notes.length > 0 && (
              <div className="mt-4 bg-amber-900/20 border border-amber-700/40 rounded-2xl p-4">
                <p className="text-sm font-medium text-amber-400 mb-2">⚠️ Important notes</p>
                <ul className="space-y-1.5">
                  {result.important_notes.map((note, i) => {
                    return (
                      <li key={i} className="text-sm text-text-secondary flex gap-2">
                        <span className="flex-shrink-0 text-amber-500">•</span>
                        <span>{note}</span>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}

            {result.sources && result.sources.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-text-secondary mb-2 font-medium uppercase tracking-wide">
                  Sources
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {result.sources.map((source, i) => {
                    return (
                      <a
                        key={i}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs bg-surface border border-border rounded-xl px-3 py-2.5 hover:border-primary transition-all"
                      >
                        <span>📄</span>
                        <span className="text-text-primary font-medium truncate flex-1">
                          {source.title}
                        </span>
                        <span className="text-text-secondary flex-shrink-0">↗</span>
                      </a>
                    )
                  })}
                </div>
              </div>
            )}

            <p className="text-xs text-text-secondary text-center mt-6 pb-2">
              {result.disclaimer}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}