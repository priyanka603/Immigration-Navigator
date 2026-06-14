import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

const SUGGESTED_QUESTIONS = [
  "Can I work while on a student visa in Ireland?",
  "What is the Critical Skills Employment Permit?",
  "How do I renew my Irish Residence Permit?",
  "What are the requirements for Irish citizenship?",
]

export default function ChatTab() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [nationality, setNationality] = useState('')
  const [currentVisa, setCurrentVisa] = useState('')
  const [showContext, setShowContext] = useState(false)
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
        disclaimer: data.disclaimer,
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
    <div className="flex flex-col h-full max-w-3xl mx-auto w-full">
      {/* Context bar */}
      <div className="px-4 pt-4">
        <button
          onClick={() => setShowContext(!showContext)}
          className="text-xs text-text-secondary flex items-center gap-1 hover:text-primary transition-colors"
        >
          <span>{showContext ? '▼' : '▶'}</span>
          Personalise answers (optional)
        </button>
        {showContext && (
          <div className="mt-2 p-3 bg-white rounded-xl border border-border flex gap-3 fade-in">
            <input
              type="text"
              placeholder="Your nationality (e.g. Indian)"
              value={nationality}
              onChange={e => setNationality(e.target.value)}
              className="flex-1 text-sm px-3 py-2 rounded-lg border border-border focus:outline-none focus:border-primary bg-background"
            />
            <input
              type="text"
              placeholder="Current visa (e.g. Stamp 2)"
              value={currentVisa}
              onChange={e => setCurrentVisa(e.target.value)}
              className="flex-1 text-sm px-3 py-2 rounded-lg border border-border focus:outline-none focus:border-primary bg-background"
            />
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-scrollbar px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="fade-in">
            <div className="text-center py-8">
              <div className="text-4xl mb-3">🍀</div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">
                Welcome to IrishPath
              </h2>
              <p className="text-text-secondary text-sm max-w-sm mx-auto">
                Ask any question about Irish immigration. I'll answer using
                official government sources.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="text-left text-sm p-3 bg-white border border-border rounded-xl hover:border-primary hover:bg-primary-light transition-all text-text-primary"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 pb-4 pt-2">
        <div className="flex gap-2 bg-white border border-border rounded-2xl p-2 shadow-sm focus-within:border-primary transition-colors">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about Irish immigration..."
            rows={1}
            className="flex-1 resize-none bg-transparent text-sm px-2 py-1.5 focus:outline-none text-text-primary placeholder-text-secondary"
            style={{ maxHeight: '120px' }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
            className="bg-primary text-white rounded-xl px-4 py-2 text-sm font-medium hover:bg-primary-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
          >
            Send →
          </button>
        </div>
        <p className="text-xs text-text-secondary text-center mt-2">
          For guidance only — always verify with official Irish government sources
        </p>
      </div>
    </div>
  )
}