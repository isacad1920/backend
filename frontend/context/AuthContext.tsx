import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { authService } from '../services/auth';
import type { StoredAuthSession, User, PermissionCode } from '../types';

interface AuthContextValue {
  user: User | null;
  permissions: PermissionCode[];
  session: StoredAuthSession | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (perm: PermissionCode | PermissionCode[]) => boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Refresh 1 minute before actual expiry (safety margin)
const EXPIRY_MARGIN_MS = 60_000;

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<StoredAuthSession | null>(authService.getSession());
  const [loading, setLoading] = useState(false);
  const [refreshTimer, setRefreshTimer] = useState<number | null>(null);
  const [expiryTimer, setExpiryTimer] = useState<number | null>(null); // forces state update at expiry for isAuthenticated consumers

  const scheduleRefresh = useCallback((s: StoredAuthSession) => {
    if (refreshTimer) window.clearTimeout(refreshTimer);
    const now = Date.now();
    const delay = Math.max(5_000, s.accessTokenExpiresAt - now - EXPIRY_MARGIN_MS); // at least 5s
    const id = window.setTimeout(async () => {
      try {
        const tokens = await authService.refreshToken();
        const updated = authService.getSession();
        if (updated) {
          setSession(updated);
          scheduleRefresh(updated);
        }
      } catch {
        // Silent failure -> will require manual interaction
      }
    }, delay);
    setRefreshTimer(id);
  }, [refreshTimer]);

  // Initialize refresh schedule
  useEffect(() => {
    if (session) scheduleRefresh(session);
    return () => { if (refreshTimer) window.clearTimeout(refreshTimer); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Schedule a re-render exactly (or just after) expiry so isAuthenticated flips without needing user interaction
  useEffect(() => {
    if (expiryTimer) {
      window.clearTimeout(expiryTimer);
      setExpiryTimer(null);
    }
    if (!session) return;
    const now = Date.now();
    const delay = Math.max(0, session.accessTokenExpiresAt - now + 50); // slight buffer to ensure past expiry
    const id = window.setTimeout(() => {
      // Trigger state change by cloning session (or clearing if already expired)
      setSession(prev => (prev && Date.now() < prev.accessTokenExpiresAt ? { ...prev } : prev));
    }, delay);
    setExpiryTimer(id);
    return () => { window.clearTimeout(id); };
  }, [session]);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    try {
      const newSession = await authService.login({ username, password });
      setSession(newSession);
      scheduleRefresh(newSession);
    } finally {
      setLoading(false);
    }
  }, [scheduleRefresh]);

  const logout = useCallback(async () => {
    await authService.logout();
    setSession(null);
    if (refreshTimer) window.clearTimeout(refreshTimer);
    if (expiryTimer) window.clearTimeout(expiryTimer);
  }, [refreshTimer]);

  const hasPermission = useCallback((perm: PermissionCode | PermissionCode[]) => {
    const list = Array.isArray(perm) ? perm : [perm];
    if (!session) return false;
    if (session.permissions.includes('all')) return true; // superuser meta permission
    return list.every(p => session.permissions.includes(p));
  }, [session]);

  const value: AuthContextValue = {
    user: session?.user || null,
    permissions: session?.permissions || [],
    session,
    loading,
    login,
    logout,
    hasPermission,
    isAuthenticated: !!session && Date.now() < session.accessTokenExpiresAt,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

// Optional guard component
export const PermissionGuard: React.FC<{ anyOf?: PermissionCode[]; allOf?: PermissionCode[]; children: React.ReactNode; fallback?: React.ReactNode }> = ({ anyOf, allOf, children, fallback = null }) => {
  const { permissions } = useAuth();
  const allow = (() => {
    if (permissions.includes('all')) return true;
    if (allOf && !allOf.every(p => permissions.includes(p))) return false;
    if (anyOf && !anyOf.some(p => permissions.includes(p))) return false;
    return true;
  })();
  return allow ? <>{children}</> : <>{fallback}</>;
};
