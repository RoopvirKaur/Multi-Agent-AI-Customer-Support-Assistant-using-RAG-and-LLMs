"use client";

import React from "react";
import {
  CreditCard,
  Wrench,
  Package,
  AlertTriangle,
  HelpCircle,
  Bot,
} from "lucide-react";

interface AgentBadgeProps {
  agentName?: string | null;
  className?: string;
}

interface BadgeConfig {
  label: string;
  bg: string;
  text: string;
  border: string;
  icon: React.ReactNode;
}

export default function AgentBadge({ agentName, className = "" }: AgentBadgeProps) {
  if (!agentName) return null;

  const normalized = agentName.toLowerCase().replace(/_agent|_support/g, "").trim();

  const configs: Record<string, BadgeConfig> = {
    billing: {
      label: "Billing Agent",
      bg: "bg-emerald-500/10",
      text: "text-emerald-400",
      border: "border-emerald-500/30",
      icon: <CreditCard className="w-3 h-3" />,
    },
    technical: {
      label: "Technical Support",
      bg: "bg-sky-500/10",
      text: "text-sky-400",
      border: "border-sky-500/30",
      icon: <Wrench className="w-3 h-3" />,
    },
    product: {
      label: "Product Specialist",
      bg: "bg-amber-500/10",
      text: "text-amber-400",
      border: "border-amber-500/30",
      icon: <Package className="w-3 h-3" />,
    },
    complaint: {
      label: "Complaint Resolution",
      bg: "bg-rose-500/10",
      text: "text-rose-400",
      border: "border-rose-500/30",
      icon: <AlertTriangle className="w-3 h-3" />,
    },
    faq: {
      label: "General FAQ",
      bg: "bg-violet-500/10",
      text: "text-violet-400",
      border: "border-violet-500/30",
      icon: <HelpCircle className="w-3 h-3" />,
    },
  };

  const config = configs[normalized] || {
    label: agentName,
    bg: "bg-indigo-500/10",
    text: "text-indigo-400",
    border: "border-indigo-500/30",
    icon: <Bot className="w-3 h-3" />,
  };

  return (
    <span
      id={`agent-badge-${normalized}`}
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.bg} ${config.text} ${config.border} shadow-sm backdrop-blur-sm ${className}`}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
}
