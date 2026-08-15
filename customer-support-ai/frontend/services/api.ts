// api.ts — Axios instance with baseURL and JWT interceptor
// Fully implemented in Phase 3
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

// Request interceptor — attach Bearer token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor — handle 401 token expiry cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response &&
      error.response.status === 401 &&
      typeof window !== "undefined"
    ) {
      const isAuthEndpoint =
        error.config?.url?.includes("/api/auth/login") ||
        error.config?.url?.includes("/api/auth/register");
      if (!isAuthEndpoint) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_profile");
      }
    }
    return Promise.reject(error);
  }
);

export default api;
