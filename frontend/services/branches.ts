import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { Branch, CreateBranchRequest, PaginationParams } from '../types';

interface BranchPerformance { branchId: number; sales: string; revenue: string; topProducts?: Array<{ productId: number; name: string; totalSold: number }>; }

export class BranchesService {
  async createBranch(branchData: CreateBranchRequest): Promise<Branch> {
    try {
      return await apiClient.post<Branch>('/branches/', branchData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getBranches(params: PaginationParams = {}): Promise<PaginatedResponse<Branch>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Branch>>(`/branches/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getBranch(branchId: number): Promise<Branch> {
    try {
      return await apiClient.get<Branch>(`/branches/${branchId}`); 
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateBranch(branchId: number, updates: Partial<Branch>): Promise<Branch> {
    try {
      return await apiClient.put<Branch>(`/branches/${branchId}`, updates); 
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteBranch(branchId: number): Promise<void> {
    try {
      await apiClient.delete(`/branches/${branchId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateBranchesStatus(branchIds: number[], isActive: boolean): Promise<void> {
    try {
      await apiClient.put('/branches/bulk/status', {
        branchIds,
        isActive,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateBranchesBulk(branches: Partial<Branch>[]): Promise<void> {
    try {
      await apiClient.put('/branches/bulk/update', { branches });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getBranchPerformance(branchId: number): Promise<BranchPerformance> {
    try {
      return await apiClient.get<BranchPerformance>(`/branches/${branchId}/performance`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getBranchInventory(branchId: number): Promise<Array<{ productId: number; name: string; quantity: number; minStock?: number }>> {
    try {
      return await apiClient.get<Array<{ productId: number; name: string; quantity: number; minStock?: number }>>(`/branches/${branchId}/inventory`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const branchesService = new BranchesService();