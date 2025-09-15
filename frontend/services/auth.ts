import { apiClient, handleApiError } from '../lib/api';
import { config } from '../config';
import type {
  AuthTokens,
  LoginResult,
  StoredAuthSession,
  User,
  PermissionCode,
  AuthSession,
  LoginCredentials
} from '../types';

// Utility: decode JWT without verifying signature (browser only, for expiry/claims)
function decodeJwt(token: string): Record<string, any> | null {
  try {
    const [, payload] = token.split('.');
    if (!payload) return null;
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
}

function buildSession(tokens: AuthTokens, user?: User, permissions?: PermissionCode[]): StoredAuthSession | null {
  if (!tokens.access_token) return null;
  const rawClaims = decodeJwt(tokens.access_token) || undefined;
  // Basic structural narrowing: ensure we at least have sub if present
  let claims: any = undefined;
  if (rawClaims && typeof rawClaims === 'object' && 'sub' in rawClaims) {
    claims = rawClaims; // minimal trust; DecodedAccessTokenClaims is indexable
  }
  // Compute absolute expiry; fall back to now + expires_in seconds
  const nowSeconds = Math.floor(Date.now() / 1000);
  const expSeconds = (claims?.exp && typeof claims.exp === 'number') ? claims.exp : (nowSeconds + (tokens.expires_in ?? 0));
  const session: StoredAuthSession = {
    schemaVersion: 1,
    user: user as User, // assume provided (backend returns user on login) - guarded by caller
    permissions: permissions || [],
    tokens,
    accessTokenExpiresAt: expSeconds * 1000,
  claims,
  };
  return session;
}

function persistSession(session: StoredAuthSession) {
  localStorage.setItem(config.storage.userKey, JSON.stringify(session));
}

function readSession(): StoredAuthSession | null {
  const raw = localStorage.getItem(config.storage.userKey);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (parsed && parsed.schemaVersion === 1) return parsed as StoredAuthSession;
  } catch {/* ignore */}
  return null;
}

function clearSession() {
  localStorage.removeItem(config.storage.userKey);
}

export class AuthService {
  async login(credentials: LoginCredentials): Promise<StoredAuthSession> {
    try {
      // Backend unified login endpoint returns envelope -> we unwrap to LoginResult
      const result = await apiClient.post<LoginResult>('/auth/login', credentials);

      // Extract tokens immediately and persist so subsequent calls (user / permissions) include Authorization header
      const tokens: AuthTokens = {
        access_token: (result as LoginResult).access_token,
        refresh_token: (result as LoginResult).refresh_token,
        token_type: (result as LoginResult).token_type,
        expires_in: (result as LoginResult).expires_in,
      };
      if (!tokens.access_token) throw new Error('Login response missing access token');
      apiClient.setToken(tokens.access_token, tokens.refresh_token);

      // If user not included (edge case), fetch /users/me
      let user = (result as any).user as User | undefined;
      if (!user) {
        try { user = await apiClient.get<User>('/users/me'); } catch (e) { console.warn('Fetch /users/me failed', e); }
      }

      // Fetch fresh effective permissions from RBAC endpoint; fall back gracefully
      let permissions: PermissionCode[] = Array.isArray((result as any).permissions) ? (result as any).permissions : [];
      try {
        if (user) {
          // Prefer normalized endpoint returning object { permissions: [...] }
            const r = await apiClient.get<any>(`/permissions/users/${user.id}`);
            if (r && Array.isArray(r.permissions)) {
              permissions = r.permissions;
            } else if (Array.isArray(r)) {
              permissions = r as PermissionCode[];
            }
        }
      } catch {
        // Fallback legacy convenience endpoint
        if (!permissions.length) {
          try { permissions = await apiClient.get<PermissionCode[]>('/permissions/mine'); } catch {/* ignore */}
        }
      }

      if (!user) throw new Error('User data missing from login response');

      const session = buildSession(tokens, user, permissions);
      if (!session) throw new Error('Failed to build session');
      persistSession(session);
      return session;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async logout(): Promise<void> {
    try {
      try { await apiClient.post('/auth/logout'); } catch (e) { /* ignore network/server logout errors */ }
    } catch (error) {
      console.warn('Logout request failed:', error);
      // Continue with local logout even if server request fails
    } finally {
      apiClient.clearToken();
      clearSession();
    }
  }

  async refreshToken(): Promise<AuthTokens> {
    try {
      const session = readSession();
      if (!session?.tokens.refresh_token) throw new Error('No refresh token available');

      const refreshed = await apiClient.post<AuthTokens>('/auth/refresh', { refresh_token: session.tokens.refresh_token });
      apiClient.setToken((refreshed as AuthTokens).access_token, (refreshed as AuthTokens).refresh_token);

      const updated = buildSession(refreshed as AuthTokens, session.user, session.permissions);
      if (updated) persistSession(updated);
      return refreshed;
    } catch (error) {
      // If refresh fails, clear stored data and redirect to login
      apiClient.clearToken();
      clearSession();
      throw new Error(handleApiError(error));
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      return await apiClient.get<User>('/users/me');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async changePassword(old_password: string, new_password: string): Promise<void> {
    try {
      await apiClient.put('/users/change-password', {
        old_password,
        new_password,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  isAuthenticated(): boolean {
    const session = readSession();
    if (!session) return false;
    if (Date.now() >= session.accessTokenExpiresAt) return false;
    return true;
  }

  getCurrentUserFromStorage(): User | null {
    const session = readSession();
    return session?.user || null;
  }

  getSession(): StoredAuthSession | null { return readSession(); }
  getPermissions(): PermissionCode[] { return this.getSession()?.permissions || []; }
}

export const authService = new AuthService();