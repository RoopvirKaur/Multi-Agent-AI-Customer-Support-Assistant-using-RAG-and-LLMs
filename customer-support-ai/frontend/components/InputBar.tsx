"use client";

import React, { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Loader2 } from "lucide-react";

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export default function InputBar({
  onSendMessage,
  isLoading,
  placeholder = "Ask about billing, warranties, technical issues, or products...",
}: InputBarProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        140
      )}px`;
    }
  }, [text]);

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      onSendMessage(text.trim());
      setText("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full bg-slate-900/90 border-t border-slate-800/80 p-4 backdrop-blur-md">
      <div className="max-w-4xl mx-auto flex items-end gap-3 bg-slate-800/70 border border-slate-700/80 rounded-2xl p-2 shadow-xl focus-within:border-indigo-500/80 focus-within:ring-1 focus-within:ring-indigo-500/30 transition-all">
        <textarea
          ref={textareaRef}
          id="chat-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none bg-transparent px-3 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none max-h-36 overflow-y-auto leading-relaxed disabled:opacity-50"
        />

        <button
          id="send-btn"
          onClick={handleSend}
          disabled={!text.trim() || isLoading}
          className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white rounded-xl font-medium text-sm transition-all duration-200 flex items-center justify-center gap-1.5 shadow-md shadow-indigo-600/30 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none shrink-0"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="hidden sm:inline">Sending</span>
            </>
          ) : (
            <>
              <span>Send</span>
              <Send className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </div>

      <div className="max-w-4xl mx-auto flex items-center justify-between text-[11px] text-slate-500 px-3 mt-2">
        <span>Press <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400">Shift + Enter</kbd> for new line</span>
        <span className="hidden sm:inline">Powered by Google Gemini & Multi-Agent RAG</span>
      </div>
    </div>
  );
}
