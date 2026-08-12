"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authService, UserProfile, AuthResponse } from "@/services/authService";

interface AuthContextType {
  token: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (name: string, email: string, password: string) => Promise<AuthResponse>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Hydrate authentication state on client mount
    if (typeof window !== "undefined") {
      const storedToken = localStorage.getItem("access_token");
      const storedProfile = localStorage.getItem("user_profile");

      if (storedToken) {
        setToken(storedToken);
        if (storedProfile) {
          try {
            setUser(JSON.parse(storedProfile));
          } catch {
            // ignore JSON parse errors
          }
        }
      }
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    const data = await authService.login(email, password);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const register = async (name: string, email: string, password: string): Promise<AuthResponse> => {
    const data = await authService.register(name, email, password);
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
