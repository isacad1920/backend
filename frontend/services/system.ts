import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { SystemInfo, Backup, BackupStatus, PaginationParams } from '../types';

interface CreateBackupRequest {
  type?: 'DB' | 'FILES' | 'FULL';
}

interface RestoreJobRequest {
  confirmToken: string;
  requestedBy: number;
}

interface RestoreJobStatus {
  id: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  progress?: number;
  message?: string;
  startedAt?: string;
  completedAt?: string;
}

export class SystemService {
  async getSystemInfo(): Promise<SystemInfo> {
    try {
      return await apiClient.get<SystemInfo>('/system/info');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getBackups(params: PaginationParams & { status?: BackupStatus; type?: string } = {}): Promise<PaginatedResponse<Backup>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.status) queryParams.append('status', params.status);
      if (params.type) queryParams.append('type', params.type);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Backup>>(`/system/backups${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createBackup(backupData: CreateBackupRequest = {}): Promise<{ id: number }> {
    try {
      return await apiClient.post<{ id: number }>('/system/backups', backupData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async startRestore(backupId: number, restoreData: RestoreJobRequest): Promise<{ jobId: number }> {
    try {
      return await apiClient.post<{ jobId: number }>(`/system/backups/${backupId}/restore/async`, restoreData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getRestoreJobStatus(jobId: number): Promise<RestoreJobStatus> {
    try {
      return await apiClient.get<RestoreJobStatus>(`/system/restore-jobs/${jobId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async verifyBackup(backupId: number): Promise<{ isValid: boolean; checksum?: string }> {
    try {
      return await apiClient.post<{ isValid: boolean; checksum?: string }>(`/system/backups/${backupId}/verify`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getHealth(): Promise<{ status: string }> {
    try {
      return await apiClient.get<{ status: string }>('/health');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async ping(): Promise<{ message: string }> {
    try {
      return await apiClient.get<{ message: string }>('/ping');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const systemService = new SystemService();