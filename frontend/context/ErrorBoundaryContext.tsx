import React from 'react';
import { mapError } from '../lib/errorMap';
import { useToast } from './ToastContext';

interface ErrorBoundaryContextValue {
  capture: (error: unknown, opts?: { silent?: boolean }) => void;
}

const ErrorBoundaryContext = React.createContext<ErrorBoundaryContextValue | undefined>(undefined);

class RootErrorBoundary extends React.Component<{ onError: (error: unknown) => void; children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error: any) { this.props.onError(error); }
  render() { return this.props.children; }
}

export const ErrorBoundaryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { push } = useToast();
  const capture = React.useCallback((error: unknown, opts?: { silent?: boolean }) => {
    if (!opts?.silent) {
      const mapped = mapError(error);
      push({ type: mapped.severity === 'success' ? 'success' : mapped.severity, title: mapped.code, message: mapped.uiMessage });
    }
    // (Optional) send to monitoring service here
  }, [push]);

  return (
    <ErrorBoundaryContext.Provider value={{ capture }}>
      <RootErrorBoundary onError={capture}>{children}</RootErrorBoundary>
    </ErrorBoundaryContext.Provider>
  );
};

export function useErrorCapture() {
  const ctx = React.useContext(ErrorBoundaryContext);
  if (!ctx) throw new Error('useErrorCapture must be used within ErrorBoundaryProvider');
  return ctx.capture;
}
