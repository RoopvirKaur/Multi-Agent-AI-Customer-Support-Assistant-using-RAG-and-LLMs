// useChat.ts — manages messages state, loading state, session state
// Fully implemented in Phase 3
"use client";
import { useState } from "react";

export function useChat() {
  const [messages, setMessages] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  return { messages, setMessages, loading, setLoading, sessionId, setSessionId };
}
