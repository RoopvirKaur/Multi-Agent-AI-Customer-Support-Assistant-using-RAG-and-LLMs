"use client";

import { useState, useEffect, useCallback } from "react";
import {
  chatService,
  ChatMessage,
  ChatSession,
  ChatResponse,
} from "@/services/chatService";

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isFetchingSessions, setIsFetchingSessions] = useState<boolean>(false);
  const [isFetchingHistory, setIsFetchingHistory] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch session history list
  const fetchSessions = useCallback(async () => {
    setIsFetchingSessions(true);
    setError(null);
    try {
      const data = await chatService.getSessions();
      setSessions(data);
    } catch (err: any) {
      console.error("Failed to load sessions:", err);
      // Suppress 401 error if not logged in yet
      if (err?.response?.status !== 401) {
        setError("Failed to load conversation history.");
      }
    } finally {
      setIsFetchingSessions(false);
    }
  }, []);

  // Fetch message history for a specific session
  const selectSession = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setIsFetchingHistory(true);
    setError(null);
    try {
      const history = await chatService.getHistory(sessionId);
      setMessages(history);
    } catch (err: any) {
      console.error("Failed to load session messages:", err);
      setError("Could not load message history for this session.");
    } finally {
      setIsFetchingHistory(false);
    }
  }, []);

  // Start a fresh new chat session
  const startNewChat = useCallback(() => {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
  }, []);

  // Delete an existing session
  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await chatService.deleteSession(sessionId);
        setSessions((prev) => prev.filter((s) => s.id !== sessionId));
        if (activeSessionId === sessionId) {
          startNewChat();
        }
      } catch (err) {
        console.error("Failed to delete session:", err);
        setError("Failed to delete conversation.");
      }
    },
    [activeSessionId, startNewChat]
  );

  // Send a message (with optimistic user turn rendering)
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      const trimmed = content.trim();
      const tempUserMsgId = `temp-${Date.now()}`;
      const nowIso = new Date().toISOString();

      // Optimistic user message
      const optimisticMsg: ChatMessage = {
        id: tempUserMsgId,
        session_id: activeSessionId || "",
        role: "user",
        content: trimmed,
        created_at: nowIso,
      };

      setMessages((prev) => [...prev, optimisticMsg]);
      setIsLoading(true);
      setError(null);

      try {
        const response: ChatResponse = await chatService.sendMessage(
          trimmed,
          activeSessionId
        );

        // Update active session ID if this was the first message
        if (!activeSessionId) {
          setActiveSessionId(response.session_id);
        }

        // Assistant response message
        const assistantMsg: ChatMessage = {
          id: response.message_id,
          session_id: response.session_id,
          role: "assistant",
          content: response.response,
          agent_name: response.agents_invoked?.[0] || "Assistant",
          intent: response.intent,
          created_at: response.timestamp,
          sources: response.sources,
        };

        setMessages((prev) => [
          ...prev.filter((m) => m.id !== tempUserMsgId),
          { ...optimisticMsg, session_id: response.session_id },
          assistantMsg,
        ]);

        // Refresh sessions list to show newly created or updated session title
        fetchSessions();
      } catch (err: any) {
        console.error("Failed to send message:", err);
        setError(
          err?.response?.data?.detail ||
            "Failed to receive response from AI support assistant."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [activeSessionId, isLoading, fetchSessions]
  );

  return {
    sessions,
    activeSessionId,
    messages,
    isLoading,
    isFetchingSessions,
    isFetchingHistory,
    error,
    fetchSessions,
    selectSession,
    startNewChat,
    deleteSession,
    sendMessage,
    setMessages,
  };
}
