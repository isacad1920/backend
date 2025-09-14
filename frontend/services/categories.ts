import { apiClient, handleApiError, PaginatedResponse } from '../lib/api';
import type { Category, PaginationParams } from '../types';

interface CreateCategoryRequest {
  name: string;
  description?: string;
}

export class CategoriesService {
  async createCategory(categoryData: CreateCategoryRequest): Promise<Category> {
    try {
      return await apiClient.post<Category>('/categories/', categoryData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCategories(params: PaginationParams = {}): Promise<PaginatedResponse<Category>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.q) queryParams.append('q', params.q);

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Category>>(`/categories/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getCategory(categoryId: number): Promise<Category> {
    try {
      return await apiClient.get<Category>(`/categories/${categoryId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async updateCategory(categoryId: number, updates: Partial<Category>): Promise<Category> {
    try {
      return await apiClient.put<Category>(`/categories/${categoryId}`, updates);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteCategory(categoryId: number): Promise<void> {
    try {
      await apiClient.delete(`/categories/${categoryId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const categoriesService = new CategoriesService();