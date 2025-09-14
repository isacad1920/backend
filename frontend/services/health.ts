import { apiClient, handleApiError } from '../lib/api';

export class HealthService {
  async checkHealth(): Promise<{ status: string }> {
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

  async testConnection(): Promise<boolean> {
    try {
      await this.ping();
      return true;
    } catch (error) {
      console.warn('Backend connection test failed:', error);
      return false;
    }
  }
}

export const healthService = new HealthService();