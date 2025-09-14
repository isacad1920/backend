import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { Account, AccountType, Currency, AccountTransferRequest, PaginationParams } from '../types';

interface CreateAccountRequest {
  name: string;
  type: AccountType;
  currency: Currency;
  branchId?: number;
}

export class AccountsService {
  async createAccount(accountData: CreateAccountRequest): Promise<Account> {
    try {
      return await apiClient.post<Account>('/accounts/', accountData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getAccounts(params: PaginationParams & { type?: AccountType; currency?: Currency; branchId?: number } = {}): Promise<PaginatedResponse<Account>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);
      if (params.type) queryParams.append('type', params.type);
      if (params.currency) queryParams.append('currency', params.currency);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Account>>(`/accounts/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getAccount(accountId: number): Promise<Account> {
    try {
      return await apiClient.get<Account>(`/accounts/${accountId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateAccount(accountId: number, updates: Partial<Account>): Promise<Account> {
    try {
      return await apiClient.put<Account>(`/accounts/${accountId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteAccount(accountId: number): Promise<void> {
    try {
      await apiClient.delete(`/accounts/${accountId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createTransfer(transferData: AccountTransferRequest): Promise<{ success: boolean; transferId?: number; message?: string; } > {
    try {
      return await apiClient.post<{ success: boolean; transferId?: number; message?: string; }, AccountTransferRequest>('/account-transfers/', transferData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const accountsService = new AccountsService();