export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`fade-in flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-[75%]">
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-sm">🍀</span>
            <span className="text-xs font-medium text-primary">IrishPath</span>
            {message.agent_used && (
              <span className="text-xs text-text-secondary bg-primary-light text-primary px-2 py-0.5 rounded-full">
                {message.agent_used} agent
              </span>
            )}
          </div>
        )}

        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-user-bubble text-text-primary border border-primary/20 rounded-tr-sm'
              : 'bg-surface border border-border text-text-primary rounded-tl-sm'
          }`}
        >
          {message.content}
        </div>
      </div>
    </div>
  )
}