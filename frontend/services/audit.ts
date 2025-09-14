import { apiClient, handleApiError,PaginatedResponse } from '../lib/api';
import type { AuditLog, PaginationParams, AuditLogSeverity } from '../types';

export class AuditService {
  async getAuditLogs(params: PaginationParams & { 
    userId?: number; 
    action?: string; 
    entityType?: string; 
    severity?: AuditLogSeverity;
    fromDate?: string;
    toDate?: string;
  } = {}): Promise<PaginatedResponse<AuditLog>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.userId) queryParams.append('userId', params.userId.toString());
      if (params.action) queryParams.append('action', params.action);
      if (params.entityType) queryParams.append('entityType', params.entityType);
      if (params.severity) queryParams.append('severity', params.severity);
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<AuditLog>>(`/audit/logs${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const auditService = new AuditService();