export default function ChatPage() {
  return (
    <main className="min-h-screen flex" style={{ background: "var(--background)" }}>
      {/* Sidebar — Session History */}
      <aside className="w-72 border-r border-slate-700 p-4 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-200">Conversations</h2>
          <button
            id="new-chat-btn"
            className="text-xs px-3 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-full transition-colors"
          >
            + New
          </button>
        </div>
        {/* Session list — populated in Phase 3 */}
        <div className="text-slate-500 text-sm text-center mt-8">
          No conversations yet
        </div>
      </aside>

      {/* Main Chat Area */}
      <section className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-slate-700 px-6 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold">
            AI
          </div>
          <div>
            <p className="font-medium">TechMart Support</p>
            <p className="text-xs text-slate-400">Multi-agent AI Assistant</p>
          </div>
        </header>

        {/* Messages — populated in Phase 3 */}
        <div id="chat-window" className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="flex justify-start">
            <div className="max-w-xl bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 text-sm">
              <p>👋 Hello! I&apos;m TechMart&apos;s AI support assistant. How can I help you today?</p>
            </div>
          </div>
        </div>

        {/* Input Bar */}
        <footer className="border-t border-slate-700 p-4">
          <div className="flex gap-3 items-end">
            <textarea
              id="chat-input"
              placeholder="Type your message... (Enter to send, Shift+Enter for newline)"
              rows={1}
              className="flex-1 resize-none bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 max-h-32"
            />
            <button
              id="send-btn"
              className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-medium transition-colors text-sm whitespace-nowrap"
            >
              Send
            </button>
          </div>
        </footer>
      </section>
    </main>
  );
}
