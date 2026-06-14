import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

const SUGGESTED_QUESTIONS = [
  "Can I work while on a student visa in Ireland?",
  "What is the Critical Skills Employment Permit?",
  "How do I renew my Irish Residence Permit?",
  "What are the requirements for Irish citizenship?",
  "Can I bring my family to Ireland on a work permit?",
  "What is the difference between Stamp 1 and Stamp 4?",
]

export default function ChatTab() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [nationality, setNationality] = useState('')
  const [currentVisa, setCurrentVisa] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const sendMessage = async (text) => {
    const messageText = text || input.trim()
    if (!messageText || isLoading) return

    setInput('')
    setIsLoading(true)
    setMessages(prev => [...prev, { role: 'user', content: messageText }])

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          nationality: nationality || null,
          current_visa: currentVisa || null,
        }),
      })

      const data = await res.json()
      if (!sessionId) setSessionId(data.session_id)

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        agent_used: data.agent_used,
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I could not connect to the server. Please make sure the backend is running.',
        sources: [],
      }])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-full" style={{ height: 'calc(100vh - 56px)' }}>

      {/* Left sidebar */}
      <div className="w-72 border-r border-border bg-surface flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-border">
          <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
            Personalise
          </p>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Your nationality"
              value={nationality}
              onChange={e => setNationality(e.target.value)}
              className="w-full text-sm px-3 py-2 rounded-lg border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary transition-colors"
            />
            <input
              type="text"
              placeholder="Current visa / stamp"
              value={currentVisa}
              onChange={e => setCurrentVisa(e.target.value)}
              className="w-full text-sm px-3 py-2 rounded-lg border border-border focus:outline-none focus:border-primary bg-surface-2 text-text-primary placeholder-text-secondary transition-colors"
            />
          </div>
        </div>

        <div className="p-4 flex-1 overflow-y-auto">
          <p className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-3">
            Suggested questions
          </p>
          <div className="space-y-1.5">
            {SUGGESTED_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                disabled={isLoading}
                className="w-full text-left text-sm p-2.5 rounded-lg hover:bg-primary-light hover:text-primary transition-all text-text-secondary leading-snug disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-border">
          <p className="text-xs text-text-secondary leading-relaxed">
            Answers grounded in official Irish government sources. Always verify before making immigration decisions.
          </p>
        </div>
      </div>

      {/* Main chat */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto chat-scrollbar p-6 space-y-5">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center fade-in">
              <div className="text-5xl mb-4">🍀</div>
              <h2 className="text-2xl font-semibold text-text-primary mb-2">
                Welcome to IrishPath
              </h2>
              <p className="text-text-secondary max-w-md">
                Ask any question about Irish immigration. I'll search official government
                sources and give you a grounded, accurate answer.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {isLoading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-border bg-surface p-4">
          <div className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about Irish immigration..."
              rows={1}
              className="flex-1 resize-none bg-surface-2 border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary text-text-primary placeholder-text-secondary transition-colors"
              style={{ maxHeight: '120px' }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || isLoading}
              className="bg-primary text-background rounded-xl px-5 py-3 text-sm font-medium hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0 h-[46px] font-semibold"
            >
              Send →
            </button>
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-72 border-l border-border bg-surface flex-shrink-0 overflow-y-auto">
        <div className="p-4 border-b border-border">
          <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">
            Sources used
          </p>
        </div>
        <div className="p-4">
          {messages.length === 0 ? (
            <p className="text-sm text-text-secondary leading-relaxed">
              Sources from official Irish government websites will appear here after each answer.
            </p>
          ) : (
            <div className="space-y-3">
              {[...messages]
                .reverse()
                .find(m => m.role === 'assistant' && m.sources?.length > 0)
                ?.sources?.map((source, i) => {
                  return (
                    <a
                      key={i}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-3 bg-surface-2 border border-border rounded-xl hover:border-primary transition-all group"
                    >
                      <p className="text-xs font-medium text-text-primary group-hover:text-primary transition-colors leading-snug">
                        {source.title}
                      </p>
                      <p className="text-xs text-text-secondary mt-1 truncate">
                        {source.url.replace('https://', '')}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs bg-primary-light text-primary px-2 py-0.5 rounded-full">
                          {source.category}
                        </span>
                        <span className="text-xs text-text-secondary">
                          {Math.round(source.relevance_score * 100)}% match
                        </span>
                      </div>
                    </a>
                  )
                }) || (
                  <p className="text-sm text-text-secondary">
                    Ask a question to see sources here.
                  </p>
                )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}