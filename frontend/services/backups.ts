import { apiClient, handleApiError } from '../lib/api';
import { ApiEnvelope, Paginated } from '../types/http';

export interface BackupRecord {
  id: number;
  type: 'FULL' | 'INCREMENTAL' | 'FILES' | 'DB';
  location: string | null;
  fileName?: string | null;
  sizeMB?: number | null;
  status: 'PENDING' | 'SUCCESS' | 'FAILED';
  errorLog?: string | null;
  createdById?: number | null;
  createdAt: string;
  completedAt?: string | null;
}

export interface BackupStats {
  total: number; successful: number; failed: number; pending: number; total_size_mb: number; last_backup_at: string | null;
}

// Result object for restore endpoints (dry run or apply). The backend may include
// a human-readable message plus arbitrary diagnostic details (table diffs, errors etc.).
// We model it permissively but expose an optional message for UI convenience.
export interface RestoreResult {
  message?: string;
  [key: string]: unknown;
}

export interface ListBackupsResponse extends Paginated<BackupRecord> {}

// Helper to normalize envelope or raw data
function extract<T>(resp: unknown): T {
  const r = resp as ApiEnvelope<T> | T;
  if (r && typeof r === 'object' && 'success' in r && 'data' in r) {
    return (r as ApiEnvelope<T>).data;
  }
  return r as T;
}

class BackupService {
  async listBackups(page=1, size=20): Promise<ListBackupsResponse> {
    try {
      const qs = new URLSearchParams({ page: String(page), per_page: String(size) });
      const resp = await apiClient.get<ApiEnvelope<Partial<ListBackupsResponse>> | Partial<ListBackupsResponse>>(`/backups?${qs.toString()}`);
      const data = extract<Partial<ListBackupsResponse>>(resp);
      return {
        items: data.items || [],
        total: data.total ?? (data.items ? data.items.length : 0),
        page: data.page ?? page,
        size: data.size ?? size,
        pagination: {
          page: data.page ?? page,
          size: data.size ?? size,
          total: data.total ?? (data.items ? data.items.length : 0)
        }
      };
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }

  async createBackup(type: BackupRecord['type'], location?: string | null): Promise<BackupRecord> {
    try {
      const payload: { type: BackupRecord['type']; location?: string | null } = { type };
      if (location) payload.location = location;
      const resp = await apiClient.post<ApiEnvelope<BackupRecord> | BackupRecord>('/backups', payload);
      return extract<BackupRecord>(resp);
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }

  async getStats(): Promise<BackupStats> {
    try {
      const resp = await apiClient.get<ApiEnvelope<BackupStats> | BackupStats>('/backups/stats');
      return extract<BackupStats>(resp);
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }

  async deleteBackup(id: number): Promise<{ deleted?: boolean } | Record<string, unknown>> {
    try {
      const resp = await apiClient.delete<ApiEnvelope<Record<string, unknown>> | Record<string, unknown>>(`/backups/${id}`);
      return extract<Record<string, unknown>>(resp);
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }

  async restoreDryRun(id: number, tables?: string[]): Promise<RestoreResult> {
    try {
      const qs = new URLSearchParams({ dry_run: 'true' });
      if (tables?.length) qs.append('tables', tables.join(','));
      const resp = await apiClient.post<ApiEnvelope<RestoreResult> | RestoreResult>(`/backups/${id}/restore2?${qs.toString()}`, {});
      return extract<RestoreResult>(resp);
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }

  async restoreApply(id: number, tables?: string[]): Promise<RestoreResult> {
    try {
      const qs = new URLSearchParams({ dry_run: 'false' });
      if (tables?.length) qs.append('tables', tables.join(','));
      const resp = await apiClient.post<ApiEnvelope<RestoreResult> | RestoreResult>(`/backups/${id}/restore2?${qs.toString()}`, {});
      return extract<RestoreResult>(resp);
    } catch (e) {
      throw new Error(handleApiError(e));
    }
  }
}

export const backupService = new BackupService();