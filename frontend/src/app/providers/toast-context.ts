import { createContext, useContext } from "react";

interface ToastContextValue {
  notify: (message: string) => void;
}

export const ToastContext = createContext<ToastContextValue | undefined>(
  undefined,
);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return ctx;
}
