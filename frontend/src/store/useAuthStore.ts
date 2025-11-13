import { create } from "zustand";

interface AuthState {
  token: string | null;
  userName: string | null;
  setToken: (token: string | null) => void;
  setUserName: (name: string | null) => void;
  reset: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userName: null,
  setToken: (token) => set({ token }),
  setUserName: (userName) => set({ userName }),
  reset: () => set({ token: null, userName: null }),
}));

