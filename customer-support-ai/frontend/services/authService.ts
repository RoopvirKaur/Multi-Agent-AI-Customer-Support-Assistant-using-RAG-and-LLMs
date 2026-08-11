// authService.ts — login, register, logout, refreshToken
// Fully implemented in Phase 3
import api from "./api";

export const authService = {
  login: async (email: string, password: string) => {
    const res = await api.post("/api/auth/login", { email, password });
    return res.data;
  },
  register: async (name: string, email: string, password: string) => {
    const res = await api.post("/api/auth/register", { name, email, password });
    return res.data;
  },
  logout: () => {
    localStorage.removeItem("access_token");
  },
  refreshToken: async () => {
    const res = await api.post("/api/auth/refresh");
    return res.data;
  },
};
