import { apiClient, handleApiError,PaginatedResponse } from '../lib/api';
import type { Customer, CreateCustomerRequest, PaginationParams, CustomerType, CustomerStatus } from '../types';

export class CustomerService {
  async createCustomer(customerData: CreateCustomerRequest): Promise<Customer> {
    try {
      return await apiClient.post<Customer>('/customers/', customerData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCustomers(params: PaginationParams & { type?: CustomerType; status?: CustomerStatus } = {}): Promise<PaginatedResponse<Customer>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);
      if (params.type) queryParams.append('type', params.type);
      if (params.status) queryParams.append('status', params.status);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Customer>>(`/customers/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCustomer(customerId: number): Promise<Customer> {
    try {
      return await apiClient.get<Customer>(`/customers/${customerId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateCustomer(customerId: number, updates: Partial<Customer>): Promise<Customer> {
    try {
      return await apiClient.put<Customer>(`/customers/${customerId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteCustomer(customerId: number): Promise<void> {
    try {
      await apiClient.delete(`/customers/${customerId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCustomerBalance(customerId: number): Promise<{ balance: string }> {
    try {
      return await apiClient.get<{ balance: string }>(`/customers/${customerId}/balance`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const customerService = new CustomerService();