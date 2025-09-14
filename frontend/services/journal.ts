import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { JournalEntry, CreateJournalEntryRequest, Account, PaginationParams } from '../types';

interface TrialBalanceResponse {
  accounts: {
    accountId: number;
    accountName: string;
    accountType: string;
    debitBalance: string;
    creditBalance: string;
  }[];
  totalDebits: string;
  totalCredits: string;
  isBalanced: boolean;
}

export class JournalService {
  async getJournalEntries(params: PaginationParams & { referenceType?: string; referenceId?: number; fromDate?: string; toDate?: string } = {}): Promise<PaginatedResponse<JournalEntry>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.referenceType) queryParams.append('referenceType', params.referenceType);
      if (params.referenceId) queryParams.append('referenceId', params.referenceId.toString());
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<JournalEntry>>(`/journal/entries${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createJournalEntry(entryData: CreateJournalEntryRequest): Promise<JournalEntry> {
    try {
      return await apiClient.post<JournalEntry>('/journal/entries', entryData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getTrialBalance(): Promise<TrialBalanceResponse> {
    try {
      return await apiClient.get<TrialBalanceResponse>('/journal/trial-balance');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getChartOfAccounts(): Promise<Account[]> {
    try {
      return await apiClient.get<Account[]>('/journal/chart-of-accounts');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const journalService = new JournalService();