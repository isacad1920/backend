import { apiClient, handleApiError } from '../lib/api';
import type { TodaySalesSummary, InventorySummary, SalesAnalytics, InventoryAnalytics } from '../types';
import { inventoryService } from './inventory';

// New real-data backed dashboard service composing multiple backend endpoints.
export class DashboardService {
  async getTodaySalesSummary(branchId?: number): Promise<TodaySalesSummary> {
    try {
      const query = branchId ? `?branch_id=${branchId}` : '';
      return await apiClient.get<TodaySalesSummary>(`/sales/today/summary${query}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getInventorySummary(): Promise<InventorySummary> {
    try {
      return await apiClient.get<InventorySummary>('/inventory/summary');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getSalesAnalytics(): Promise<SalesAnalytics> {
    try {
      return await apiClient.get<SalesAnalytics>('/financial/analytics/sales');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getInventoryAnalytics(): Promise<InventoryAnalytics> {
    try {
      return await apiClient.get<InventoryAnalytics>('/financial/analytics/inventory');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Combined high-level stats (legacy consumers can shift to granular calls above)
  async getAggregatedStats(options: { branchId?: number; includeLowStock?: boolean } = {}): Promise<{
    today: TodaySalesSummary;
    inventory: InventorySummary;
    lowStock?: { product_id: number | null; name: string | null; sku: string | null; quantity: number; min_stock?: number | null }[];
  }> {
    try {
      const [today, inventory, lowStockBatch] = await Promise.all([
        this.getTodaySalesSummary(options.branchId),
        this.getInventorySummary(),
        options.includeLowStock ? inventoryService.getLowStockBatch({ page_size: 50 }) : Promise.resolve(null)
      ]);
      return { 
        today, 
        inventory, 
        lowStock: lowStockBatch ? (lowStockBatch.items || []).map(i => ({
          product_id: i.product_id,
          name: i.name,
          sku: i.sku,
          quantity: i.quantity,
          min_stock: undefined
        })) : undefined
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const dashboardService = new DashboardService();