// Shared HTTP / API envelope & pagination types
// These mirror the standardized backend response structure (success, data, message, error, meta, timestamp)

export interface ApiErrorObject {
  code?: string;
  detail?: string;
  field_errors?: Record<string, string[]>;
  [key: string]: unknown;
}

export interface ApiEnvelope<T> {
  success: boolean;
  message?: string | null;
  data: T;
  error?: ApiErrorObject | null;
  meta?: Record<string, unknown> | null;
  timestamp?: string;
}

export interface Paginated<T> {
  pagination: any;
  items: T[];
  page: number;
  size: number;
  total: number;
}

// Legacy alias some services used prior to consolidation; now a simple type alias to avoid empty interface lint
export type PaginatedResponse<T> = Paginated<T>;

// Generic function type for service fetchers
export type ApiFetcher<T> = () => Promise<T>;

// Helper to narrow possible undefined data shapes
export type Maybe<T> = T | null | undefined;

// Extract inner data type from an envelope
export type UnwrapEnvelope<E> = E extends ApiEnvelope<infer D> ? D : never;

// Common list shape (non-paginated)
export interface ListResult<T> {
  items: T[];
}

// Convenience type for ID fields
export type ID = string | number;
