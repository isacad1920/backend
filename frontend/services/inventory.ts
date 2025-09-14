import { apiClient, handleApiError } from '../lib/api';
import type { InventorySummary, UnifiedInventoryItem } from '../types';

interface UnifiedInventoryItemsResponseMeta {
  pagination: {
    page: number;
    size: number;
    total: number;
    page_count: number;
  };
  filters: {
    status: string;
    search?: string | null;
    category_id?: number | null;
  };
  expansions: string[];
}

export class InventoryService {
  async getSummary(): Promise<InventorySummary> {
    try {
      return await apiClient.get<InventorySummary>('/inventory/summary');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getItems(params: {
    status?: 'all' | 'low_stock' | 'dead_stock';
    search?: string;
    category_id?: number;
    page?: number;
    size?: number;
    low_stock_threshold?: number;
    expand?: string[]; // valuation,sales_timeseries
  } = {}): Promise<{ items: UnifiedInventoryItem[]; meta: UnifiedInventoryItemsResponseMeta }> {
    try {
      const queryParams = new URLSearchParams();
      if (params.status) queryParams.append('status', params.status);
      if (params.search) queryParams.append('search', params.search);
      if (params.category_id) queryParams.append('category_id', params.category_id.toString());
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.low_stock_threshold !== undefined) queryParams.append('low_stock_threshold', params.low_stock_threshold.toString());
      if (params.expand && params.expand.length) queryParams.append('expand', params.expand.join(','));

      const query = queryParams.toString();
      // Backend returns envelope with data (list) + meta we need to preserve meta
      const data = await apiClient.get<any>(`/inventory/items${query ? `?${query}` : ''}`);
      return {
        items: data as UnifiedInventoryItem[],
        meta: (data as any)?.meta as UnifiedInventoryItemsResponseMeta
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getLowStockBatch(params: {
    page?: number;
    page_size?: number;
    threshold?: number;
    search?: string;
    category_id?: number;
  } = {}): Promise<{ items: UnifiedInventoryItem[]; pagination: { page: number; page_size: number; total: number; page_count: number }; threshold?: number; default_threshold?: number; }> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.page_size) queryParams.append('page_size', params.page_size.toString());
      if (params.threshold !== undefined) queryParams.append('threshold', params.threshold.toString());
      if (params.search) queryParams.append('search', params.search);
      if (params.category_id) queryParams.append('category_id', params.category_id.toString());
      const query = queryParams.toString();
      const data = await apiClient.get<any>(`/inventory/low-stock/batch${query ? `?${query}` : ''}`);
      // Endpoint returns envelope with pagination meta and meta_extra including thresholds.
      return data as any;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const inventoryService = new InventoryService();
