import { useState } from 'react'

export default function ChecklistTab() {
  const [goal, setGoal] = useState('')
  const [nationality, setNationality] = useState('')
  const [currentStatus, setCurrentStatus] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const generateChecklist = async () => {
    if (!goal.trim() || !nationality.trim() || !currentStatus.trim()) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/checklist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          nationality,
          current_status: currentStatus,
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch {
      setError('Could not connect to the server. Please make sure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto w-full px-4 py-6 overflow-y-auto h-full chat-scrollbar">
      <div className="bg-white rounded-2xl border border-border p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-text-primary mb-1">
          Generate your immigration checklist
        </h2>
        <p className="text-sm text-text-secondary mb-6">
          Tell us your situation and we'll create a personalised step-by-step plan.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">
              What is your goal?
            </label>
            <input
              type="text"
              value={goal}
              onChange={e => setGoal(e.target.value)}
              placeholder="e.g. Apply for Critical Skills Employment Permit"
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-primary bg-background text-sm transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">
              Your nationality
            </label>
            <input
              type="text"
              value={nationality}
              onChange={e => setNationality(e.target.value)}
              placeholder="e.g. Indian, Brazilian, Chinese"
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-primary bg-background text-sm transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-1.5">
              Current status in Ireland
            </label>
            <input
              type="text"
              value={currentStatus}
              onChange={e => setCurrentStatus(e.target.value)}
              placeholder="e.g. Student Stamp 2, Not in Ireland yet"
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:border-primary bg-background text-sm transition-colors"
            />
          </div>

          <button
            onClick={generateChecklist}
            disabled={!goal.trim() || !nationality.trim() || !currentStatus.trim() || isLoading}
            className="w-full bg-primary text-white rounded-xl py-3 text-sm font-medium hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating your checklist...
              </span>
            ) : (
              'Generate my checklist →'
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 fade-in">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 fade-in space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text-primary">
              Your personalised plan
            </h3>
            <span className="text-xs text-text-secondary bg-primary-light px-3 py-1 rounded-full">
              {result.steps.length} steps
            </span>
          </div>

          {result.steps.map((step, i) => {
            return (
              <div
                key={i}
                className="bg-white rounded-2xl border border-border p-5 shadow-sm"
              >
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-primary text-white text-sm font-semibold flex items-center justify-center flex-shrink-0">
                    {step.step_number}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-text-primary mb-1">
                      {step.title}
                    </h4>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {step.description}
                    </p>

                    {step.documents_required.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-text-primary mb-1.5">
                          Documents required:
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {step.documents_required.map((doc, j) => {
                            return (
                              <span
                                key={j}
                                className="text-xs bg-background border border-border px-2.5 py-1 rounded-full text-text-secondary"
                              >
                                {doc}
                              </span>
                            )
                          })}
                        </div>
                      </div>
                    )}

                    <div className="flex flex-wrap gap-4 mt-3">
                      {step.fee && (
                        <span className="text-xs text-accent font-medium">
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

          {result.important_notes.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
              <p className="text-sm font-medium text-text-primary mb-2">
                ⚠️ Important notes
              </p>
              <ul className="space-y-1">
                {result.important_notes.map((note, i) => {
                  return (
                    <li key={i} className="text-sm text-text-secondary flex gap-2">
                      <span>•</span>
                      <span>{note}</span>
                    </li>
                  )
                })}
              </ul>
            </div>
          )}

          {result.sources.length > 0 && (
            <div>
              <p className="text-xs text-text-secondary mb-2">Sources:</p>
              <div className="space-y-1">
                {result.sources.map((source, i) => {
                  return (
                    <a
                      key={i}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-xs bg-white border border-border rounded-lg px-3 py-2 hover:border-primary hover:bg-primary-light transition-all"
                    >
                      <span>📄</span>
                      <span className="text-text-primary font-medium truncate">
                        {source.title}
                      </span>
                      <span className="text-text-secondary ml-auto flex-shrink-0">↗</span>
                    </a>
                  )
                })}
              </div>
            </div>
          )}

          <p className="text-xs text-text-secondary text-center py-2">
            {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  )
}