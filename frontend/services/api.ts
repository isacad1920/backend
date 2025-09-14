// Base API configuration and utilities
import { config } from '../config';

const API_BASE_URL = config.apiUrl;

// Backend canonical envelope types
export interface ApiEnvelope<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  meta: {
    app_version?: string;
    correlation_id?: string;
  };
  timestamp: string;
}

export interface PaginationMeta {
  total: number;
  page: number;
  size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public code?: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseURL: string;
  private token: string | null = null;
  private refreshing: Promise<string | null> | null = null; // single-flight refresh promise

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.loadToken();
  }

  private loadToken() {
    const savedUser = localStorage.getItem(config.storage.userKey);
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        this.token = userData.access_token || userData.token;
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem(config.storage.userKey);
      }
    }
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem(config.storage.userKey);
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Add timeout to prevent hanging requests
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);

    const requestInit: RequestInit = {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    if (this.token) {
      requestInit.headers = {
        ...requestInit.headers,
        Authorization: `Bearer ${this.token}`,
      };
    }

    try {
      let response = await fetch(url, requestInit);
      clearTimeout(timeoutId);
      
      const contentType = response.headers.get('content-type');
      let responseData: ApiEnvelope<T>;
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        // Handle non-JSON responses
  const textData = await response.text();
        responseData = {
          success: response.ok,
          message: response.ok ? 'Success' : 'Error',
          data: textData as unknown as T,
          meta: {},
          timestamp: new Date().toISOString()
        };
      }

      // If unauthorized attempt refresh (only once per request)
      if ((response.status === 401 || responseData.error?.code === 'HTTP_401') && endpoint !== '/auth/refresh' && endpoint !== '/auth/login') {
        // Trigger refresh if not already in-flight
        if (!this.refreshing) {
          try {
            // dynamic import to avoid circular import at module top
            const { authService } = await import('./auth');
            this.refreshing = authService.refreshToken()
              .then(tokens => { this.setToken(tokens.access_token); return tokens.access_token; })
              .catch(err => { this.clearToken(); return null; })
              .finally(() => { this.refreshing = null; });
          } catch {
            this.refreshing = null;
          }
        }
        const newToken = await this.refreshing;
        if (newToken) {
          // retry original request once with new token
          requestInit.headers = { ...(requestInit.headers||{}), Authorization: `Bearer ${newToken}` };
          const retryResp = await fetch(url, requestInit);
          response = retryResp;
          const retryCT = retryResp.headers.get('content-type');
          if (retryCT && retryCT.includes('application/json')) {
            responseData = await retryResp.json();
          } else {
            const textData = await retryResp.text();
            responseData = {
              success: retryResp.ok,
              message: retryResp.ok ? 'Success' : 'Error',
              data: textData as unknown as T,
              meta: {},
              timestamp: new Date().toISOString()
            };
          }
        }
      }

      if (!response.ok || !responseData.success) {
        const errorMessage = responseData.error?.message || responseData.message || `HTTP error! status: ${response.status}`;
        const errorCode = responseData.error?.code || `HTTP_${response.status}`;
        throw new ApiError(response.status, errorMessage, errorCode, responseData.error?.details);
      }

      if (typeof responseData.data === 'undefined') {
        throw new ApiError(response.status, 'Missing data in success envelope', 'NO_DATA');
      }
      return responseData.data as T;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle abort errors (timeout)
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError(408, 'Request timeout', 'TIMEOUT');
      }
      
      // Network or other errors
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error');
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T, B = unknown>(endpoint: string, data?: B): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T, B = unknown>(endpoint: string, data?: B): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T, B = unknown>(endpoint: string, data?: B): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// Helper function to handle API errors consistently
export const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      // Token expired or invalid
      apiClient.clearToken();
      window.location.reload(); // Force re-login
      return 'Session expired. Please log in again.';
    }
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

// Helper function for handling async operations with loading states
export async function withLoading<T>(
  operation: () => Promise<T>,
  setLoading: (loading: boolean) => void
): Promise<T | null> {
  try {
    setLoading(true);
    const result = await operation();
    return result;
  } catch (error) {
    console.error('Operation failed:', error);
    throw error;
  } finally {
    setLoading(false);
  }
}

// Optional helper returning a Result wrapper instead of throwing
import type { Result } from '../types/result';
export async function safeRequest<T>(op: () => Promise<T>): Promise<Result<T>> {
  try {
    const value = await op();
    return { ok: true, value } as const;
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : 'Unknown error' } as const;
  }
}