import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

const EXAMPLE_SCENARIOS = [
  "I received a letter saying my Stamp 2 permission is expiring in 30 days",
  "I got a letter from INIS saying my application for an IRP renewal is under review",
  "I received a refusal letter for my Critical Skills Employment Permit application",
  "My employer gave me a letter about sponsoring my work permit — what does it mean?",
]

const MarkdownContent = ({ content }) => (
  <ReactMarkdown
    components={{
      p: ({ children }) => (
        <p className="mb-2 last:mb-0 text-sm text-text-primary leading-relaxed">
          {children}
        </p>
      ),
      ul: ({ children }) => (
        <ul className="mb-2 space-y-1 list-none">{children}</ul>
      ),
      li: ({ children }) => (
        <li className="flex gap-2 text-sm text-text-primary">
          <span className="text-primary flex-shrink-0 mt-0.5">•</span>
          <span>{children}</span>
        </li>
      ),
      strong: ({ children }) => (
        <strong className="font-semibold text-text-primary">{children}</strong>
      ),
      h3: ({ children }) => (
        <h3 className="font-semibold text-text-primary mb-1 mt-3 first:mt-0 text-sm">
          {children}
        </h3>
      ),
      table: ({ children }) => (
        <div className="overflow-x-auto my-2">
          <table className="text-xs w-full border-collapse">{children}</table>
        </div>
      ),
      th: ({ children }) => (
        <th className="text-left px-3 py-2 bg-surface-2 border border-border font-medium text-text-primary">
          {children}
        </th>
      ),
      td: ({ children }) => (
        <td className="px-3 py-2 border border-border text-text-secondary">
          {children}
        </td>
      ),
    }}
  >
    {content}
  </ReactMarkdown>
)

export default function DocumentTab() {
  const [documentText, setDocumentText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  const explainDocument = async () => {
    if (!documentText.trim()) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Please explain this immigration document or situation in plain English and tell me what action I need to take: ${documentText}`,
          session_id: sessionId,
        }),
      })

      const data = await res.json()
      if (!sessionId) setSessionId(data.session_id)
      setResult(data)
    } catch {
      setError('Could not connect to the server. Please make sure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExample = (example) => {
    setDocumentText(example)
    setResult(null)
    setError(null)
  }

  return (
    <div className="flex h-full" style={{ height: 'calc(100vh - 56px)' }}>

      {/* Left — input */}
      <div className="w-96 border-r border-border bg-surface flex flex-col flex-shrink-0">
        <div className="p-6 flex-1 overflow-y-auto chat-scrollbar">
          <h2 className="text-base font-semibold text-text-primary mb-1">
            Explain a document
          </h2>
          <p className="text-sm text-text-secondary mb-6 leading-relaxed">
            Paste text from an immigration letter or form, or describe your situation.
            We'll explain what it means and what you need to do next.
          </p>

          <div className="mb-4">
            <label className="block text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
              Your document or situation
            </label>
            <textarea
              value={documentText}
              onChange={e => setDocumentText(e.target.value)}
              placeholder="Paste the text from your letter or describe your situation here..."
              rows={10}
              className="w-full px-3 py-3 rounded-xl border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary text-sm transition-colors resize-none leading-relaxed"
            />
          </div>

          <button
            onClick={explainDocument}
            disabled={!documentText.trim() || isLoading}
            className="w-full bg-primary text-background rounded-xl py-3 text-sm font-semibold hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
                Analysing...
              </span>
            ) : (
              'Explain this →'
            )}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-700/50 rounded-xl text-sm text-red-400">
              {error}
            </div>
          )}

          <div className="mt-6">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
              Try an example
            </p>
            <div className="space-y-2">
              {EXAMPLE_SCENARIOS.map((example, i) => {
                return (
                  <button
                    key={i}
                    onClick={() => handleExample(example)}
                    className="w-full text-left text-xs p-2.5 rounded-lg hover:bg-primary-light hover:text-primary transition-all text-text-secondary leading-snug"
                  >
                    {example}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-border">
          <p className="text-xs text-text-secondary leading-relaxed">
            For guidance only. Always verify with official Irish government sources before taking action.
          </p>
        </div>
      </div>

      {/* Right — explanation */}
      <div className="flex-1 overflow-y-auto chat-scrollbar p-6">
        {!result && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-5xl mb-4">📄</div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              Plain English explanations
            </h3>
            <p className="text-text-secondary max-w-sm leading-relaxed">
              Paste text from an INIS letter, a permit document, or describe
              your situation. We'll explain what it means and exactly what
              you need to do.
            </p>
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-text-secondary text-sm">
              Analysing your document and searching official sources...
            </p>
          </div>
        )}

        {result && (
          <div className="max-w-2xl fade-in">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-lg">🍀</span>
              <span className="text-sm font-medium text-primary">IrishPath</span>
              <span className="text-xs bg-primary-light text-primary px-2 py-0.5 rounded-full">
                document agent
              </span>
            </div>

            <div className="bg-surface border border-border rounded-2xl p-6 mb-4">
              <MarkdownContent content={result.answer} />
            </div>

            {result.sources && result.sources.length > 0 && (
              <div>
                <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
                  Sources
                </p>
                <div className="space-y-2">
                  {result.sources.map((source, i) => {
                    return (
                      <a
                        key={i}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 bg-surface border border-border rounded-xl hover:border-primary transition-all group"
                      >
                        <span className="text-base">📄</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-text-primary group-hover:text-primary transition-colors truncate">
                            {source.title}
                          </p>
                          <p className="text-xs text-text-secondary truncate mt-0.5">
                            {source.url.replace('https://', '')}
                          </p>
                        </div>
                        <span className="text-xs bg-primary-light text-primary px-2 py-0.5 rounded-full flex-shrink-0">
                          {source.category}
                        </span>
                      </a>
                    )
                  })}
                </div>
              </div>
            )}

            <p className="text-xs text-text-secondary text-center mt-6">
              {result.disclaimer}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}