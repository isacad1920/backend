import React from 'react';
import { usePermissions } from '../context/PermissionsContext';
import { useAuth } from '../context/AuthContext';
import type { PermissionCode } from '../types';

interface RequireProps {
  anyOf?: PermissionCode[];
  allOf?: PermissionCode[];
  not?: PermissionCode[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
  loadingFallback?: React.ReactNode;
  // When true, hides (renders nothing) instead of fallback if unauthorized
  hideIfUnauthorized?: boolean;
}

function evaluate(perms: PermissionCode[], anyOf?: PermissionCode[], allOf?: PermissionCode[], not?: PermissionCode[]): boolean {
  if (perms.includes('all')) return true;
  if (not && not.some(p => perms.includes(p))) return false;
  if (allOf && !allOf.every(p => perms.includes(p))) return false;
  if (anyOf && !anyOf.some(p => perms.includes(p))) return false;
  return true;
}

export const Require: React.FC<RequireProps> = ({ anyOf, allOf, not, children, fallback = null, loadingFallback = null, hideIfUnauthorized }) => {
  const { permissions, loading } = usePermissions();
  const { user } = useAuth();
  if (loading) return <>{loadingFallback}</>;
  // ADMIN short-circuit: full access
  if (user?.role === 'ADMIN') return <>{children}</>;
  const allowed = evaluate(permissions, anyOf, allOf, not);
  if (allowed) return <>{children}</>;
  if (hideIfUnauthorized) return null;
  return <>{fallback}</>;
};

export function usePermissionCheck() {
  const { permissions } = usePermissions();
  const { user } = useAuth();
  return React.useCallback((perm: PermissionCode | PermissionCode[]) => {
    if (user?.role === 'ADMIN') return true;
    const list = Array.isArray(perm) ? perm : [perm];
    if (permissions.includes('all')) return true;
    return list.every(p => permissions.includes(p));
  }, [permissions, user?.role]);
}
