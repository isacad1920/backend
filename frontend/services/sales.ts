import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { Sale, CreateSaleRequest, PaginationParams, SaleStatus, PaymentMethod, TodaySalesSummary } from '../types';

interface SalePaymentRecord {
  id: number;
  saleId: number;
  accountId: number;
  amount: string; // keeping as string if API returns decimal strings
  method: PaymentMethod;
  currency: string;
  reference?: string;
  createdAt: string;
}

interface AddPaymentRequest {
  accountId: number;
  amount: string;
  method: PaymentMethod;
  currency: string;
  reference?: string;
}

interface AddPaymentResponse {
  success: boolean;
  payment: SalePaymentRecord;
  remainingBalance?: string;
}

interface SaleReturnItem {
  saleItemId: number;
  quantity: number;
  refundAmount: string; // decimal string
}

interface SaleReturnRecord {
  id: number;
  saleId: number;
  items: SaleReturnItem[];
  type: 'REFUND_ONLY' | 'EXCHANGE';
  reason: string;
  totalRefund: string;
  createdAt: string;
}

interface CreateReturnRequest {
  originalId: number;
  items: SaleReturnItem[];
  type: 'REFUND_ONLY' | 'EXCHANGE';
  reason: string;
}

interface CreateSaleReturnRequest {
  items: SaleReturnItem[];
  type: 'REFUND_ONLY' | 'EXCHANGE';
  reason: string;
}

interface CreateReturnResponse {
  success: boolean;
  return: SaleReturnRecord;
}

interface SalesFilters extends PaginationParams {
  branchId?: number;
  customerId?: number;
  from?: string;
  to?: string;
  status?: SaleStatus;
}

export class SalesService {
  async getTodaySummary(branchId?: number): Promise<TodaySalesSummary> {
    try {
      const query = branchId ? `?branch_id=${branchId}` : '';
      return await apiClient.get<TodaySalesSummary>(`/sales/today/summary${query}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
  async createSale(saleData: CreateSaleRequest): Promise<{ saleId: number; saleNumber: string; totalAmount: string; paidAmount: string; dueAmount: string; status: SaleStatus }> {
    try {
      return await apiClient.post('/sales/', saleData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getSales(params: SalesFilters = {}): Promise<PaginatedResponse<Sale>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());
      if (params.customerId) queryParams.append('customerId', params.customerId.toString());
      if (params.from) queryParams.append('from', params.from);
      if (params.to) queryParams.append('to', params.to);
      if (params.status) queryParams.append('status', params.status);
      if (params.q) queryParams.append('q', params.q);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Sale>>(`/sales/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getSale(saleId: number): Promise<Sale> {
    try {
      return await apiClient.get<Sale>(`/sales/${saleId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateSale(saleId: number, updates: Partial<Sale>): Promise<Sale> {
    try {
      return await apiClient.put<Sale>(`/sales/${saleId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async addPaymentToSale(saleId: number, payment: {
    accountId: number;
    amount: string;
    method: PaymentMethod;
    currency: string;
  }): Promise<AddPaymentResponse> {
    try {
      return await apiClient.post<AddPaymentResponse>(`/sales/${saleId}/payments`, payment);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getSalePayments(saleId: number): Promise<SalePaymentRecord[]> {
    try {
      return await apiClient.get<SalePaymentRecord[]>(`/sales/${saleId}/payments`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createReturn(returnData: CreateReturnRequest): Promise<CreateReturnResponse> {
    try {
      return await apiClient.post<CreateReturnResponse>('/returns/', returnData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createSaleReturn(saleId: number, returnData: CreateSaleReturnRequest): Promise<CreateReturnResponse> {
    try {
      return await apiClient.post<CreateReturnResponse>(`/sales/${saleId}/returns`, returnData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const salesService = new SalesService();