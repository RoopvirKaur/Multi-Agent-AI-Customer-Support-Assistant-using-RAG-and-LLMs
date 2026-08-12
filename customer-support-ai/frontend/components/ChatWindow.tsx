"use client";

import React, { useRef, useEffect } from "react";
import {
  Sparkles,
  CreditCard,
  Wrench,
  Package,
  ShieldCheck,
  Bot,
} from "lucide-react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import { ChatMessage } from "@/services/chatService";

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectPrompt?: (prompt: string) => void;
}

export default function ChatWindow({
  messages,
  isLoading,
  onSelectPrompt,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const quickPrompts = [
    {
      title: "Refunds & Invoices",
      desc: "How do I request a refund under TechMart policy?",
      icon: <CreditCard className="w-4 h-4 text-emerald-400" />,
      tag: "Billing",
    },
    {
      title: "Device Troubleshooting",
      desc: "How do I troubleshoot Bluetooth pairing issues on my SmartHub?",
      icon: <Wrench className="w-4 h-4 text-sky-400" />,
      tag: "Technical",
    },
    {
      title: "Product Specs & Pricing",
      desc: "What are the specs and tiers for TechMart SmartHub Pro?",
      icon: <Package className="w-4 h-4 text-amber-400" />,
      tag: "Product",
    },
    {
      title: "Warranty Protection",
      desc: "What does the 2-year TechMart warranty cover?",
      icon: <ShieldCheck className="w-4 h-4 text-violet-400" />,
      tag: "Warranty",
    },
  ];

  return (
    <div
      id="chat-window"
      className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 min-h-0"
    >
      {messages.length === 0 ? (
        <div className="max-w-3xl mx-auto py-12 px-4 flex flex-col items-center text-center space-y-8 animate-fade-in">
          {/* Hero Icon & Title */}
          <div className="space-y-3">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center text-white mx-auto shadow-2xl shadow-indigo-500/40">
              <Bot className="w-8 h-8" />
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-100">
              Welcome to <span className="gradient-text">TechMart AI</span>
            </h2>
            <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
              Your 24/7 intelligent multi-agent customer assistant. Ask about policies, billing, products, or technical support.
            </p>
          </div>

          {/* Quick Start Prompt Grid */}
          <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-left">
            {quickPrompts.map((item, idx) => (
              <button
                key={idx}
                onClick={() => onSelectPrompt?.(item.desc)}
                className="glass-panel p-4 rounded-2xl border border-slate-700/60 hover:border-indigo-500/50 hover:bg-slate-800/80 transition-all duration-200 group flex flex-col justify-between space-y-2 shadow-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center border border-slate-700/80">
                    {item.icon}
                  </div>
                  <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                    {item.tag}
                  </span>
                </div>
                <div>
                  <h3 className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">
                    {item.desc}
                  </p>
                </div>
              </button>
            ))}
          </div>

          {/* Live Multi-Agent Info Banner */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/80 text-[11px] text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Autonomous Intent Routing & RAG Grounded Retrieval</span>
          </div>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {isLoading && <TypingIndicator agentName="TechMart Assistant" />}
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
