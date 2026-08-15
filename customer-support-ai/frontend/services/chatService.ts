/**
 * Chat Service
 * Handles API interactions with /api/chat and /api/history endpoints.
 */

import api from "./api";

export interface SourceCitation {
  document: string;
  page?: number | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  agent_name?: string | null;
  intent?: string[] | null;
  created_at: string;
  sources?: SourceCitation[];
}

export interface ChatResponse {
  message_id: string;
  response: string;
  agents_invoked: string[];
  intent: string[];
  session_id: string;
  timestamp: string;
  sources: SourceCitation[];
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export const chatService = {
  sendMessage: async (
    message: string,
    sessionId?: string | null
  ): Promise<ChatResponse> => {
    const res = await api.post<ChatResponse>("/api/chat/message", {
      message,
      session_id: sessionId || null,
    });
    return res.data;
  },

  getSessions: async (): Promise<ChatSession[]> => {
    const res = await api.get<ChatSession[]>("/api/chat/sessions");
    return res.data;
  },

  createSession: async (title?: string): Promise<ChatSession> => {
    const res = await api.post<ChatSession>("/api/chat/sessions", {
      title: title || "New Conversation",
    });
    return res.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/api/chat/sessions/${sessionId}`);
  },

  getHistory: async (sessionId: string): Promise<ChatMessage[]> => {
    const res = await api.get<ChatMessage[]>(`/api/history/${sessionId}`);
    return res.data;
  },
};
