"use client";

import React from "react";
import Link from "next/link";
import {
  Bot,
  CreditCard,
  Wrench,
  Package,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  Zap,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function Home() {
  const { isAuthenticated } = useAuth();

  const agentCards = [
    {
      title: "Billing & Accounts",
      desc: "Instant invoice lookups, subscription adjustments, and refund policy guidance.",
      icon: <CreditCard className="w-5 h-5 text-emerald-400" />,
      color: "border-emerald-500/30 bg-emerald-500/5",
    },
    {
      title: "Technical Support",
      desc: "Step-by-step troubleshooting, firmware upgrades, and error diagnosis.",
      icon: <Wrench className="w-5 h-5 text-sky-400" />,
      color: "border-sky-500/30 bg-sky-500/5",
    },
    {
      title: "Product Specialist",
      desc: "Deep product specifications, compatibility checks, and pricing tier comparisons.",
      icon: <Package className="w-5 h-5 text-amber-400" />,
      color: "border-amber-500/30 bg-amber-500/5",
    },
    {
      title: "Complaint Resolution",
      desc: "Empathetic conflict de-escalation, grievance tracking, and ticket handoff.",
      icon: <AlertTriangle className="w-5 h-5 text-rose-400" />,
      color: "border-rose-500/30 bg-rose-500/5",
    },
    {
      title: "General FAQ & Policies",
      desc: "24/7 answers to store policies, warranty protection, and store hours.",
      icon: <HelpCircle className="w-5 h-5 text-violet-400" />,
      color: "border-violet-500/30 bg-violet-500/5",
    },
    {
      title: "FAISS Vector RAG",
      desc: "Every response grounded in authoritative TechMart documentation PDFs.",
      icon: <Zap className="w-5 h-5 text-indigo-400" />,
      color: "border-indigo-500/30 bg-indigo-500/5",
    },
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden flex flex-col justify-between">
      {/* Background glow decorations */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-600/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[300px] bg-violet-600/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Navigation Header */}
      <nav className="max-w-6xl mx-auto w-full px-6 py-6 flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center text-white shadow-xl shadow-indigo-600/30">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-extrabold text-base tracking-tight text-slate-100">
              TechMart <span className="text-indigo-400">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
              Multi-Agent Assistant
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              href="/chat"
              className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5"
            >
              <span>Open Chat</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-12 pb-16 text-center space-y-8 relative z-10 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs text-indigo-300 font-medium shadow-md">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Next-Generation Autonomous Customer Intelligence</span>
        </div>

        <div className="space-y-4 max-w-3xl mx-auto">
          <h2 className="text-4xl sm:text-6xl font-black tracking-tight leading-tight">
            Customer Support Powered by{" "}
            <span className="gradient-text">Coordinated AI Agents</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg leading-relaxed max-w-2xl mx-auto">
            Experience intelligent routing and instant, accurate resolutions for TechMart Electronics. Grounded in enterprise documentation and verified policies.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link
            href={isAuthenticated ? "/chat" : "/register"}
            className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-2xl text-sm shadow-xl shadow-indigo-600/30 transition-all flex items-center justify-center gap-2"
          >
            <span>{isAuthenticated ? "Go to Workspace" : "Try Assistant Now"}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-4 bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white font-semibold rounded-2xl text-sm transition-all"
          >
            Customer Login
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-12 text-left">
          {agentCards.map((card, idx) => (
            <div
              key={idx}
              className={`p-5 rounded-2xl border ${card.color} glass-panel space-y-2.5 transition-all duration-200 hover:-translate-y-0.5`}
            >
              <div className="w-9 h-9 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-center">
                {card.icon}
              </div>
              <h3 className="font-bold text-sm text-slate-100">{card.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{card.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 px-6 text-center text-xs text-slate-500 relative z-10">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>TechMart Electronics Enterprise Support Platform</span>
          </div>
          <p>© 2026 TechMart AI. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
