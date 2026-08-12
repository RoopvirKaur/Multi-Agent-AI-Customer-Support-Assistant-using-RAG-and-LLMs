"use client";

import React from "react";
import { Bot, Sparkles } from "lucide-react";

interface TypingIndicatorProps {
  agentName?: string;
}

export default function TypingIndicator({ agentName = "TechMart AI" }: TypingIndicatorProps) {
  return (
    <div
      id="typing-indicator"
      className="flex items-start gap-3 max-w-2xl animate-fade-in"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shrink-0 shadow-md shadow-indigo-500/20">
        <Bot className="w-4 h-4" />
      </div>

      <div className="glass-panel rounded-2xl rounded-tl-sm px-4 py-3 border border-slate-700/60 shadow-lg">
        <div className="flex items-center gap-2 mb-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span className="text-xs text-indigo-300 font-medium">
            {agentName} is thinking...
          </span>
        </div>

        <div className="flex items-center gap-1.5 py-1">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "0ms" }} />
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "150ms" }} />
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: "300ms" }} />
        </div>
      </div>
    </div>
  );
}
