"use client";

import { useState, useEffect, useCallback, createContext, useContext } from "react";

interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

interface ToastContextType {
  toast: (message: string, type?: "success" | "error" | "info") => void;
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

let nextId = 0;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: "success" | "error" | "info" = "info") => {
    const id = nextId++;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      {/* Toast container */}
      <div className="fixed bottom-6 right-6 z-[200] flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto px-4 py-3 rounded-xl shadow-lg border text-[13px] font-medium flex items-center gap-2.5 animate-in slide-in-from-right ${
              t.type === "success" ? "bg-[#f0fdf4] border-[#bbf7d0] text-[#15803d]" :
              t.type === "error" ? "bg-[#fef2f2] border-[#fecaca] text-[#b91c1c]" :
              "bg-white border-[#e8e5e0] text-[#1a1a1a]"
            }`}
            style={{ animation: "toast-in 0.3s ease-out" }}
          >
            {t.type === "success" && <span className="w-5 h-5 bg-[#15803d] text-white rounded-full flex items-center justify-center text-[10px] font-bold shrink-0">&#10003;</span>}
            {t.type === "error" && <span className="w-5 h-5 bg-[#b91c1c] text-white rounded-full flex items-center justify-center text-[10px] font-bold shrink-0">!</span>}
            {t.type === "info" && <span className="w-5 h-5 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-[10px] font-bold shrink-0">i</span>}
            {t.message}
            <button onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))} className="text-current opacity-40 hover:opacity-100 ml-2 shrink-0">&times;</button>
          </div>
        ))}
      </div>
      <style>{`@keyframes toast-in { from { opacity: 0; transform: translateX(24px); } to { opacity: 1; transform: translateX(0); } }`}</style>
    </ToastContext.Provider>
  );
}
