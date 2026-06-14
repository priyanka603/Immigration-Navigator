export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`fade-in flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] ${isUser ? 'order-1' : 'order-2'}`}>
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-sm">🍀</span>
            <span className="text-xs font-medium text-primary">IrishPath</span>
            {message.agent_used && (
              <span className="text-xs text-text-secondary bg-primary-light px-2 py-0.5 rounded-full">
                {message.agent_used} agent
              </span>
            )}
          </div>
        )}

        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-primary text-white rounded-tr-sm'
              : 'bg-white border border-border text-text-primary rounded-tl-sm shadow-sm'
          }`}
        >
          {message.content}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-text-secondary px-1">Sources:</p>
            {message.sources.slice(0, 3).map((source, i) => {
              return (
                <a
                  key={i}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs bg-white border border-border rounded-lg px-3 py-2 hover:border-primary hover:bg-primary-light transition-all group"
                >
                  <span className="text-base">📄</span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-text-primary truncate group-hover:text-primary transition-colors">
                      {source.title}
                    </p>
                    <p className="text-text-secondary truncate">{source.url}</p>
                  </div>
                  <span className="text-text-secondary flex-shrink-0">↗</span>
                </a>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}