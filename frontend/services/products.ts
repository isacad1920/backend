import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { Product, CreateProductRequest, PaginationParams, Stock, StockAdjustmentRequest } from '../types';

// Lightweight domain result placeholders (can be replaced with concrete backend types when available)
interface StockAdjustmentResult {
  success: boolean;
  adjustmentId?: number;
  updatedStock?: Stock;
  message?: string;
}

interface InventoryItemSummary {
  id: number;
  productId: number;
  sku?: string;
  name?: string;
  quantity: number;
  minStock?: number;
  maxStock?: number;
}

interface StockLevelSummary {
  productId: number;
  inStock: number;
  reserved?: number;
  available?: number;
}

interface LowStockBatchItem extends InventoryItemSummary {
  status: 'low' | 'out';
}

export class ProductService {
  async createProduct(productData: CreateProductRequest): Promise<Product> {
    try {
      return await apiClient.post<Product>('/products/', productData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getProducts(params: PaginationParams & { category?: number; branchId?: number } = {}): Promise<PaginatedResponse<Product>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);
      if (params.category) queryParams.append('category', params.category.toString());
      if (params.branchId) queryParams.append('branchId', params.branchId.toString());

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Product>>(`/products/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getProduct(productId: number): Promise<Product> {
    try {
      return await apiClient.get<Product>(`/products/${productId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateProduct(productId: number, updates: Partial<Product>): Promise<Product> {
    try {
      return await apiClient.put<Product>(`/products/${productId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteProduct(productId: number): Promise<void> {
    try {
      await apiClient.delete(`/products/${productId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async adjustStock(adjustment: StockAdjustmentRequest): Promise<StockAdjustmentResult> {
    try {
      return await apiClient.post<StockAdjustmentResult>('/products/stock/adjust', adjustment);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async adjustProductStock(productId: number, adjustment: StockAdjustmentRequest): Promise<StockAdjustmentResult> {
    try {
      return await apiClient.post<StockAdjustmentResult>(`/products/${productId}/adjust-stock`, adjustment);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async bulkAdjustStock(adjustments: StockAdjustmentRequest[]): Promise<Array<StockAdjustmentResult>> {
    try {
      return await apiClient.post<Array<StockAdjustmentResult>>('/products/stock/bulk-adjust', { adjustments });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  // Inventory methods
  async getInventoryItems(): Promise<InventoryItemSummary[]> {
    try {
      return await apiClient.get<InventoryItemSummary[]>('/inventory/items');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getStockLevels(): Promise<StockLevelSummary[]> {
    try {
      return await apiClient.get<StockLevelSummary[]>('/inventory/stock-levels');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getLowStockItems(): Promise<LowStockBatchItem[]> {
    try {
      return await apiClient.get<LowStockBatchItem[]>('/inventory/low-stock');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getLowStockBatch(): Promise<LowStockBatchItem[]> {
    try {
      return await apiClient.get<LowStockBatchItem[]>('/inventory/low-stock/batch');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createStockAdjustment(adjustment: {
    stockId: number;
    adjustment: number;
    reason: string;
  }): Promise<Stock> {
    try {
      return await apiClient.post<Stock>('/inventory/stock-adjustments', adjustment);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const productService = new ProductService();