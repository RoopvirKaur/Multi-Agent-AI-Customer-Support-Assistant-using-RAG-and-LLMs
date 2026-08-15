"use client";

import React, { useState } from "react";
import {
  MessageSquare,
  Plus,
  Trash2,
  LogOut,
  User,
  Bot,
  Search,
} from "lucide-react";
import { ChatSession } from "@/services/chatService";
import { useAuth } from "@/hooks/useAuth";

interface HistoryPanelProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  isLoadingSessions?: boolean;
}

export default function HistoryPanel({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  isLoadingSessions,
}: HistoryPanelProps) {
  const { user, logout } = useAuth();
  const [searchTerm, setSearchTerm] = useState("");

  const filteredSessions = sessions.filter((s) =>
    s.title?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <aside className="w-80 h-full bg-slate-950/80 border-r border-slate-800/80 flex flex-col justify-between backdrop-blur-xl shrink-0 select-none">
      {/* Top Section */}
      <div className="p-4 space-y-4 flex flex-col flex-1 min-h-0">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-600/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 leading-none">
              TechMart Support
            </h1>
            <span className="text-[11px] text-indigo-400 font-medium">
              Multi-Agent AI Engine
            </span>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          id="new-chat-btn"
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all duration-200"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>

        {/* Search Conversations */}
        {sessions.length > 3 && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        )}

        {/* Sessions List Header */}
        <div className="flex items-center justify-between px-2 pt-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          <span>Conversations</span>
          <span className="text-slate-500">{sessions.length}</span>
        </div>

        {/* Sessions Scrollable List */}
        <div className="flex-1 overflow-y-auto space-y-1 pr-1 min-h-0">
          {isLoadingSessions ? (
            <div className="flex flex-col gap-2 p-2">
              <div className="h-10 rounded-lg bg-slate-800/40 animate-pulse" />
              <div className="h-10 rounded-lg bg-slate-800/40 animate-pulse" />
              <div className="h-10 rounded-lg bg-slate-800/40 animate-pulse" />
            </div>
          ) : filteredSessions.length === 0 ? (
            <div className="text-center py-10 px-4 text-xs text-slate-500">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 text-slate-600/50" />
              <p>No conversations found</p>
              <p className="text-[11px] text-slate-600 mt-1">
                Start a new chat to ask questions
              </p>
            </div>
          ) : (
            filteredSessions.map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <div
                  key={session.id}
                  id={`session-item-${session.id}`}
                  onClick={() => onSelectSession(session.id)}
                  className={`group flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl cursor-pointer text-xs transition-all duration-150 ${
                    isActive
                      ? "bg-indigo-600/20 text-indigo-200 border border-indigo-500/30 font-medium"
                      : "text-slate-400 hover:bg-slate-900 hover:text-slate-200 border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <MessageSquare
                      className={`w-3.5 h-3.5 shrink-0 ${
                        isActive ? "text-indigo-400" : "text-slate-500"
                      }`}
                    />
                    <span className="truncate">{session.title || "Untitled Chat"}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* User Profile & Logout Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/90">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
              <User className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">
                {user?.name || "Customer"}
              </p>
              <p className="text-[10px] text-slate-400 truncate">
                {user?.email || "Signed In"}
              </p>
            </div>
          </div>

          <button
            id="logout-btn"
            onClick={logout}
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
