"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Menu,
  X,
  Bot,
  Sparkles,
  ShieldAlert,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useChat } from "@/hooks/useChat";
import HistoryPanel from "@/components/HistoryPanel";
import ChatWindow from "@/components/ChatWindow";
import InputBar from "@/components/InputBar";

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: isAuthLoading, user } = useAuth();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const {
    sessions,
    activeSessionId,
    messages,
    isLoading: isChatSending,
    isFetchingSessions,
    error: chatError,
    fetchSessions,
    selectSession,
    startNewChat,
    deleteSession,
    sendMessage,
  } = useChat();

  // Authentication Guard
  useEffect(() => {
    if (!isAuthLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isAuthLoading, router]);

  // Load session list on initial mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchSessions();
    }
  }, [isAuthenticated, fetchSessions]);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
    setMobileSidebarOpen(false);
  };

  const handleNewChat = () => {
    startNewChat();
    setMobileSidebarOpen(false);
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
        <span className="text-sm">Authenticating session...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <main className="h-screen w-screen flex overflow-hidden bg-slate-950 text-slate-100 relative">
      {/* Desktop Sidebar */}
      <div className="hidden md:block h-full">
        <HistoryPanel
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onDeleteSession={deleteSession}
          isLoadingSessions={isFetchingSessions}
        />
      </div>

      {/* Mobile Drawer Backdrop & Sidebar */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="relative z-10 w-80 max-w-[85vw] h-full shadow-2xl animate-fade-in">
            <HistoryPanel
              sessions={sessions}
              activeSessionId={activeSessionId}
              onSelectSession={handleSelectSession}
              onNewChat={handleNewChat}
              onDeleteSession={deleteSession}
              isLoadingSessions={isFetchingSessions}
            />
          </div>
        </div>
      )}

      {/* Main Chat Interface */}
      <section className="flex-1 flex flex-col h-full min-w-0 bg-slate-950/60 relative">
        {/* Header Bar */}
        <header className="h-16 border-b border-slate-800/80 px-4 sm:px-6 flex items-center justify-between glass-panel-subtle shrink-0 z-10">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
              className="p-2 -ml-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 md:hidden"
              title="Toggle sidebar"
            >
              {mobileSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shrink-0 shadow-md shadow-indigo-600/30">
              <Bot className="w-5 h-5" />
            </div>

            <div className="min-w-0">
              <h2 className="text-xs sm:text-sm font-bold text-slate-100 truncate">
                {activeSession ? activeSession.title : "TechMart Support Assistant"}
              </h2>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Active AI Router
                </span>
                <span className="hidden sm:inline text-slate-600">•</span>
                <span className="hidden sm:inline text-[11px] text-slate-400 truncate">
                  5 Specialized Agents Ready
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions Header Right */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchSessions()}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              title="Refresh conversation list"
            >
              <RefreshCw className={`w-4 h-4 ${isFetchingSessions ? "animate-spin text-indigo-400" : ""}`} />
            </button>
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-[11px] text-indigo-300 font-medium">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              <span>Gemini 1.5 Grounded</span>
            </div>
          </div>
        </header>

        {/* Global Error Banner */}
        {chatError && (
          <div className="px-4 py-2 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{chatError}</span>
          </div>
        )}

        {/* Messages Scroll Area */}
        <ChatWindow
          messages={messages}
          isLoading={isChatSending}
          onSelectPrompt={(prompt) => sendMessage(prompt)}
        />

        {/* Bottom Input Field */}
        <InputBar
          onSendMessage={(msg) => sendMessage(msg)}
          isLoading={isChatSending}
        />
      </section>
    </main>
  );
}
