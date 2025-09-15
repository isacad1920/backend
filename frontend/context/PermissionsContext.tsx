import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { apiClient } from '../lib/api';
import { authService } from '../services/auth';
import { config } from '../config';
import type { PermissionCode } from '../types';

interface PermissionsContextValue {
  permissions: PermissionCode[];
  loading: boolean;
  refresh: () => Promise<void>;
  has: (perm: PermissionCode | PermissionCode[], opts?: { any?: boolean }) => boolean;
}

const PermissionsContext = createContext<PermissionsContextValue | undefined>(undefined);

export const PermissionsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const initialPerms = authService.getPermissions();
  // If no permissions stored yet, seed with an empty array (will trigger fallback display logic in Sidebar)
  const [permissions, setPermissions] = useState<PermissionCode[]>(initialPerms);
  const [loading, setLoading] = useState(false);

  const fetchPermissions = useCallback(async () => {
    setLoading(true);
    try {
      // Endpoint variant: prefer /permissions/users/{id} if user known, else fallback to /permissions/mine
      const user = authService.getCurrentUserFromStorage();
      let data: PermissionCode[] = [];
      if (user) {
        try {
          const result = await apiClient.get<{ permissions: PermissionCode[] }>(`/permissions/users/${user.id}`);
          if (Array.isArray((result as any).permissions)) data = (result as any).permissions;
          else if (Array.isArray(result)) data = result as any;
        } catch {
          try { data = await apiClient.get<PermissionCode[]>(`/permissions/mine`); } catch {/* ignore */}
        }
      }
      if (!data.length) {
        // Final fallback to session cached permissions
        data = authService.getPermissions();
      }
      setPermissions(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // On mount and whenever authentication state changes (storage event), refresh
    fetchPermissions();
    const onStorage = (e: StorageEvent) => {
      if (e.key === config.storage.userKey) fetchPermissions();
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [fetchPermissions]);

  const has = useCallback((perm: PermissionCode | PermissionCode[], opts?: { any?: boolean }) => {
    const list = Array.isArray(perm) ? perm : [perm];
    if (permissions.includes('all')) return true;
    return opts?.any ? list.some(p => permissions.includes(p)) : list.every(p => permissions.includes(p));
  }, [permissions]);

  const value: PermissionsContextValue = {
    permissions,
    loading,
    refresh: fetchPermissions,
    has,
  };

  return <PermissionsContext.Provider value={value}>{children}</PermissionsContext.Provider>;
};

export function usePermissions(): PermissionsContextValue {
  const ctx = useContext(PermissionsContext);
  if (!ctx) throw new Error('usePermissions must be used inside PermissionsProvider');
  return ctx;
}

export function usePermission(perm: PermissionCode | PermissionCode[], opts?: { any?: boolean }) {
  const { has, loading } = usePermissions();
  return { allowed: has(perm, opts), loading };
}

export const Permission: React.FC<{ perm: PermissionCode | PermissionCode[]; any?: boolean; fallback?: React.ReactNode; children: React.ReactNode }> = ({ perm, any, fallback = null, children }) => {
  const { allowed } = usePermission(perm, { any });
  return allowed ? <>{children}</> : <>{fallback}</>;
};
