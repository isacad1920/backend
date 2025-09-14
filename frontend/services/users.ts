import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { User, CreateUserRequest, Role, PaginationParams } from '../types';

interface UserStatistics {
  totalUsers: number;
  activeUsers: number;
  inactiveUsers: number;
  byRole: Array<{ role: Role; count: number }>;
  byBranch?: Array<{ branchId: number; count: number }>;
}

export class UsersService {
  async createUser(userData: CreateUserRequest): Promise<User> {
    try {
      return await apiClient.post<User>('/users/', userData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getUsers(params: PaginationParams & { role?: Role; branchId?: number } = {}): Promise<PaginatedResponse<User>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);
      if (params.role) queryParams.append('role', params.role);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<User>>(`/users/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getUser(userId: number): Promise<User> {
    try {
      return await apiClient.get<User>(`/users/${userId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getUserPermissions(userId: number): Promise<string[]> {
    try {
      return await apiClient.get<string[]>(`/users/${userId}/permissions`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateUser(userId: number, updates: Partial<User>): Promise<User> {
    try {
      return await apiClient.put<User>(`/users/${userId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteUser(userId: number): Promise<void> {
    try {
      await apiClient.delete(`/users/${userId}`);
    } catch (error) {
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

  async updateProfile(updates: Partial<User>): Promise<User> {
    try {
      return await apiClient.put<User>('/users/profile', updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      await apiClient.put('/users/change-password', {
        old_password: oldPassword,
        new_password: newPassword,
      });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async resetPassword(userId: number): Promise<void> {
    try {
      await apiClient.post(`/users/${userId}/reset-password`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getUserStatistics(): Promise<UserStatistics> {
    try {
      return await apiClient.get<UserStatistics>('/users/statistics');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const usersService = new UsersService();