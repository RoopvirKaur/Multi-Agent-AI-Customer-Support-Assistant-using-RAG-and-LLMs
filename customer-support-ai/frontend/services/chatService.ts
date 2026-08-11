// chatService.ts — sendMessage, getSessions, getHistory
// Fully implemented in Phase 3
import api from "./api";

export const chatService = {
  sendMessage: async (sessionId: string, message: string) => {
    const res = await api.post("/api/chat/message", { session_id: sessionId, message });
    return res.data;
  },
  getSessions: async () => {
    const res = await api.get("/api/chat/sessions");
    return res.data;
  },
  getHistory: async (sessionId: string) => {
    const res = await api.get(`/api/history/${sessionId}`);
    return res.data;
  },
};
