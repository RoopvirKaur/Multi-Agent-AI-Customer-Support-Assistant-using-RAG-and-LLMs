"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { User, Bot, Check, Copy } from "lucide-react";
import AgentBadge from "./AgentBadge";
import { ChatMessage } from "@/services/chatService";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formattedTime = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (isUser) {
    return (
      <div
        id={`msg-user-${message.id}`}
        className="flex items-start justify-end gap-3 max-w-3xl ml-auto animate-slide-up"
      >
        <div className="flex flex-col items-end gap-1 max-w-xl">
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-500 text-white rounded-2xl rounded-tr-sm px-5 py-3 text-sm shadow-md shadow-indigo-600/20 leading-relaxed break-words">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          <span className="text-[10px] text-slate-500 pr-1">{formattedTime}</span>
        </div>

        <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-slate-300 shrink-0 shadow-sm">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  return (
    <div
      id={`msg-assistant-${message.id}`}
      className="flex items-start gap-3 max-w-3xl animate-slide-up group"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shrink-0 shadow-md shadow-indigo-500/20">
        <Bot className="w-4 h-4" />
      </div>

      <div className="flex flex-col gap-1.5 flex-1 min-w-0">
        {/* Agent Badges header */}
        <div className="flex items-center gap-2 flex-wrap">
          {message.agent_name && (
            <AgentBadge agentName={message.agent_name} />
          )}
          {message.intent &&
            message.intent.length > 0 &&
            message.intent
              .filter((i) => i !== message.agent_name)
              .map((it) => <AgentBadge key={it} agentName={it} />)}
          <span className="text-[10px] text-slate-500 ml-auto">{formattedTime}</span>
        </div>

        {/* Message Content with Markdown */}
        <div className="glass-panel rounded-2xl rounded-tl-sm p-4 text-sm text-slate-200 border border-slate-700/60 shadow-lg leading-relaxed relative">
          <div className="prose prose-invert max-w-none text-sm leading-relaxed space-y-2">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Quick Copy Button */}
          <button
            onClick={handleCopy}
            className="absolute top-2 right-2 p-1.5 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-slate-800/80 opacity-0 group-hover:opacity-100 transition-opacity"
            title="Copy response"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
