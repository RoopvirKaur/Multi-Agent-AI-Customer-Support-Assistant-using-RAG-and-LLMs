/**
 * Authentication Service
 * Handles API calls to FastAPI /api/auth endpoints.
 */

import api from "./api";

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>("/api/auth/login", {
      email,
      password,
    });
    if (res.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("user_profile", JSON.stringify(res.data.user));
    }
    return res.data;
  },

  register: async (
    name: string,
    email: string,
    password: string
  ): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>("/api/auth/register", {
      email,
      password,
      name: name || undefined,
    });
    if (res.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("user_profile", JSON.stringify(res.data.user));
    }
    return res.data;
  },

  getMe: async (): Promise<UserProfile> => {
    const res = await api.get<UserProfile>("/api/auth/me");
    if (typeof window !== "undefined") {
      localStorage.setItem("user_profile", JSON.stringify(res.data));
    }
    return res.data;
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>("/api/auth/refresh");
    if (res.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", res.data.access_token);
    }
    return res.data;
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_profile");
    }
  },
};
