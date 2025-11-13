import * as RadixToast from "@radix-ui/react-toast";
import { ReactNode, useCallback, useMemo, useState } from "react";
import { ToastContext } from "./toast-context";

interface ToastProviderProps {
  children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const notify = useCallback((text: string) => {
    setMessage(text);
    setOpen(true);
  }, []);

  const value = useMemo(
    () => ({
      notify,
    }),
    [notify],
  );

  return (
    <ToastContext.Provider value={value}>
      <RadixToast.Provider swipeDirection="right">
        {children}
        <RadixToast.Root
          className="rounded-lg bg-neutral-900 px-4 py-3 text-neutral-50 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in"
          open={open}
          onOpenChange={setOpen}
        >
          <RadixToast.Title className="text-sm font-medium">
            {message ?? "Уведомление"}
          </RadixToast.Title>
        </RadixToast.Root>
        <RadixToast.Viewport className="fixed bottom-4 right-4 z-50 flex w-72 flex-col gap-2" />
      </RadixToast.Provider>
    </ToastContext.Provider>
  );
}
