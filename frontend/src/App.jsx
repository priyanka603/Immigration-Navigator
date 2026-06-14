import { useState } from 'react'
import ChatTab from './components/ChatTab'
import ChecklistTab from './components/ChecklistTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-border px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🍀</span>
          <div>
            <h1 className="text-lg font-semibold text-text-primary">IrishPath</h1>
            <p className="text-xs text-text-secondary">Irish Immigration Navigator</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-secondary bg-primary-light px-3 py-1.5 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-primary inline-block"></span>
          Powered by official Irish government sources
        </div>
      </header>

      {/* Tab switcher */}
      <div className="bg-white border-b border-border px-6">
        <div className="flex gap-1 max-w-3xl mx-auto">
          {[
            { id: 'chat', label: '💬 Ask a question' },
            { id: 'checklist', label: '✅ Get a checklist' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? <ChatTab /> : <ChecklistTab />}
      </main>
    </div>
  )
}