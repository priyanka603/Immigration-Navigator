import ReactMarkdown from 'react-markdown'

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
          {isUser ? (
            message.content
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="mb-2 space-y-1 list-none">{children}</ul>
                ),
                li: ({ children }) => (
                  <li className="flex gap-2">
                    <span className="text-primary flex-shrink-0 mt-0.5">•</span>
                    <span>{children}</span>
                  </li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-text-primary">
                    {children}
                  </strong>
                ),
                h3: ({ children }) => (
                  <h3 className="font-semibold text-text-primary mb-1 mt-3 first:mt-0">
                    {children}
                  </h3>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="text-xs w-full border-collapse">
                      {children}
                    </table>
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
              {message.content}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  )
}