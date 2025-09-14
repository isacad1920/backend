import { apiClient, handleApiError } from '../lib/api';
import type { SalesAnalytics, InventoryAnalytics, FinancialReport } from '../types';

interface ReportParams {
  fromDate?: string;
  toDate?: string;
  branchId?: number;
}

interface ExportParams extends ReportParams {
  format?: 'JSON' | 'PDF' | 'CSV';
}

interface BalanceSheetEntry { account: string; debit: string; credit: string; balance: string; }
interface BalanceSheetReport { dateRange: { from?: string; to?: string }; entries: BalanceSheetEntry[]; totalAssets?: string; totalLiabilities?: string; }
interface IncomeStatementReport { dateRange: { from?: string; to?: string }; revenue: string; expenses: string; profit: string; }
interface CashFlowSection { name: string; amount: string; }
interface CashFlowReport { dateRange: { from?: string; to?: string }; sections: CashFlowSection[]; netCashFlow: string; }
interface FinancialRatio { name: string; value: string; category?: string; }
interface FinancialRatiosReport { dateRange: { from?: string; to?: string }; ratios: FinancialRatio[]; }

export class ReportsService {
  // Financial Reports
  async getBalanceSheet(params: ReportParams = {}): Promise<BalanceSheetReport> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
  return await apiClient.get<BalanceSheetReport>(`/financial/balance-sheet${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getIncomeStatement(params: ReportParams = {}): Promise<IncomeStatementReport> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
  return await apiClient.get<IncomeStatementReport>(`/financial/income-statement${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCashFlow(params: ReportParams = {}): Promise<CashFlowReport> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
  return await apiClient.get<CashFlowReport>(`/financial/cash-flow${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getProfitLoss(params: ReportParams = {}): Promise<FinancialReport> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<FinancialReport>(`/financial/profit-loss${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async exportFinancialReport(reportType: string, params: ExportParams = {}): Promise<{ exportId: string; status: 'QUEUED' | 'COMPLETED'; url?: string; } > {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());
      if (params.format) queryParams.append('format', params.format);

      const query = queryParams.toString();
  return await apiClient.post<{ exportId: string; status: 'QUEUED' | 'COMPLETED'; url?: string; }, { reportType: string }>(`/financial/export${query ? `?${query}` : ''}`, { reportType });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Analytics
  async getSalesAnalytics(params: ReportParams = {}): Promise<SalesAnalytics> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<SalesAnalytics>(`/financial/analytics/sales${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getInventoryAnalytics(params: ReportParams = {}): Promise<InventoryAnalytics> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<InventoryAnalytics>(`/financial/analytics/inventory${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getFinancialRatios(params: ReportParams = {}): Promise<FinancialRatiosReport> {
    try {
      const queryParams = new URLSearchParams();
      if (params.fromDate) queryParams.append('fromDate', params.fromDate);
      if (params.toDate) queryParams.append('toDate', params.toDate);
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
  return await apiClient.get<FinancialRatiosReport>(`/financial/ratios${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const reportsService = new ReportsService();