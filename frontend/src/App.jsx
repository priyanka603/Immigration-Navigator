import { useState } from 'react'
import ChatTab from './components/ChatTab'
import ChecklistTab from './components/ChecklistTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="bg-surface border-b border-border px-8 py-0 flex items-center justify-between sticky top-0 z-10 h-14">
        <div className="flex items-center gap-3">
          <span className="text-xl">🍀</span>
          <div>
            <h1 className="text-base font-semibold text-text-primary leading-tight">IrishPath</h1>
            <p className="text-xs text-text-secondary leading-tight">Irish Immigration Navigator</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <nav className="flex gap-1">
            {[
              { id: 'chat', label: '💬 Ask a question' },
              { id: 'checklist', label: '✅ Get a checklist' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-text-secondary hover:text-text-primary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary inline-block"></span>
            Powered by official Irish government sources
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? <ChatTab /> : <ChecklistTab />}
      </main>
    </div>
  )
}