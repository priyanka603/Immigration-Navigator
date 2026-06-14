export default function TypingIndicator() {
  return (
    <div className="fade-in flex justify-start">
      <div className="bg-white border border-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="text-sm">🍀</span>
          <div className="flex gap-1 ml-1">
            {[0, 1, 2].map(i => (
              <span
                key={i}
                className="typing-dot w-1.5 h-1.5 rounded-full bg-primary inline-block"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
          <span className="text-xs text-text-secondary ml-1">Searching official sources...</span>
        </div>
      </div>
    </div>
  )
}