import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "../services/api";

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,

      login: async (username, password) => {
        const { data } = await api.post("/api/auth/login", { username, password });
        set({ token: data.access_token, refreshToken: data.refresh_token });
        const me = await api.get("/api/auth/me", {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
        set({ user: me.data });
      },

      logout: () => set({ token: null, refreshToken: null, user: null }),

      setTokens: (access, refresh) => set({ token: access, refreshToken: refresh }),
    }),
    {
      name: "auth-storage",
      partialize: (s) => ({ token: s.token, refreshToken: s.refreshToken, user: s.user }),
    }
  )
);