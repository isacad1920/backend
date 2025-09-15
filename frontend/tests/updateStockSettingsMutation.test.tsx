import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, act } from '@testing-library/react';
import React from 'react';
import { useUpdateInventoryStockSettings } from '../hooks/useInventoryQueries';
import { inventoryService } from '../services/inventory';
import { ToastProvider } from '../context/ToastContext';

// Mock inventory service
vi.mock('../services/inventory', () => ({
  inventoryService: {
    updateProduct: vi.fn().mockResolvedValue({ ok: true })
  }
}));

// Utility to seed cache with an items query result
function seedItemsCache(qc: QueryClient, product: any) {
  const key = ['inventory','items',{ page:1, size:25, status:'all', search:undefined, category_id:undefined }];
  qc.setQueryData(key, { items: [product], meta: { pagination: { page:1, size:25, total:1, page_count:1 }, filters: { status:'all' }, expansions: [] } });
  return key;
}

const wrapperFactory = (seed?: boolean, productOverrides: Partial<any> = {}) => {
  const qc = new QueryClient();
  let originalProduct = {
    product_id: 42,
    name: 'Widget',
    quantity: 10,
    min_stock: 2,
    max_stock: 20,
    reorder_point: 5,
    ...productOverrides
  };
  let key: any;
  if (seed) key = seedItemsCache(qc, originalProduct);
  const Wrapper = ({ children }: any) => <ToastProvider><QueryClientProvider client={qc}>{children}</QueryClientProvider></ToastProvider>;
  return { Wrapper, qc, key, originalProduct };
};

describe('useUpdateInventoryStockSettings optimistic behavior', () => {
  beforeEach(() => vi.resetAllMocks());

  it('optimistically updates item fields then invalidates items key on settle', async () => {
    const { Wrapper, qc, key, originalProduct } = wrapperFactory(true);
    const invalidateSpy = vi.spyOn(qc, 'invalidateQueries');

    const { result } = renderHook(() => useUpdateInventoryStockSettings(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.mutateAsync({ productId: 42, minStock: 3, maxStock: 25, reorderPoint: 6 });
    });

    const cached = qc.getQueryData<any>(key);
    expect(cached.items[0].min_stock).toBe(3);
    expect(cached.items[0].max_stock).toBe(25);
    expect(cached.items[0].reorder_point).toBe(6);
    expect(inventoryService.updateProduct).toHaveBeenCalledWith(42, { min_stock: 3, max_stock: 25, reorder_point: 6 });
    expect(invalidateSpy).toHaveBeenCalled();
  });

  it('rolls back on error', async () => {
    (inventoryService.updateProduct as any).mockRejectedValueOnce(new Error('fail'));
    const { Wrapper, qc, key, originalProduct } = wrapperFactory(true);
    const { result } = renderHook(() => useUpdateInventoryStockSettings(), { wrapper: Wrapper });

    await act(async () => {
      await expect(result.current.mutateAsync({ productId: 42, minStock: 4 })).rejects.toThrow();
    });

    const cached = qc.getQueryData<any>(key);
    expect(cached.items[0].min_stock).toBe(originalProduct.min_stock); // rolled back
  });
});
