import React, { createContext, useContext, useState, useCallback } from 'react';

export interface Toast {
  id: string;
  type?: 'info' | 'success' | 'error' | 'warning';
  title?: string;
  message: string;
  duration?: number; // ms
}

interface ToastContextValue {
  toasts: Toast[];
  push: (toast: Omit<Toast, 'id'>) => void;
  dismiss: (id: string) => void;
  clear: () => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts(t => t.filter(toast => toast.id !== id));
  }, []);

  const push = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2,8)}`;
    const full: Toast = { id, duration: 4000, type: 'info', ...toast };
    setToasts(t => [...t, full]);
    if (full.duration) {
      setTimeout(() => dismiss(id), full.duration);
    }
  }, [dismiss]);

  const clear = useCallback(() => setToasts([]), []);

  return (
    <ToastContext.Provider value={{ toasts, push, dismiss, clear }}>
      {children}
      {/* Portal container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-80">
        {toasts.map(t => (
          <div key={t.id} className={`rounded border p-3 shadow text-sm backdrop-blur-md bg-white/10 border-white/20 text-white animate-in fade-in slide-in-from-bottom-1`}> 
            <div className="flex justify-between items-start gap-3">
              <div className="flex-1">
                {t.title && <p className="font-medium mb-0.5">{t.title}</p>}
                <p className="text-white/70 whitespace-pre-wrap leading-snug">{t.message}</p>
              </div>
              <button onClick={() => dismiss(t.id)} className="text-white/50 hover:text-white text-xs">✕</button>
            </div>
            <div className="mt-2 h-1 bg-white/10 rounded overflow-hidden">
              <div className={`h-full ${t.type === 'success' ? 'bg-green-400/70' : t.type === 'error' ? 'bg-red-400/70' : t.type === 'warning' ? 'bg-amber-400/70' : 'bg-blue-400/70'}`} style={{ width: '100%' }} />
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
