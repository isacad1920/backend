import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, act } from '@testing-library/react';
import { useUpdateInventoryStockSettings } from '../hooks/useInventoryQueries';
import { inventoryService } from '../services/inventory';
import { ToastProvider } from '../context/ToastContext';

vi.mock('../services/inventory', () => ({
  inventoryService: {
    updateProduct: vi.fn().mockResolvedValue({ ok: true })
  }
}));

function seedItemsCache(qc: QueryClient, product: any) {
  const key = ['inventory','items',{ page:1, size:25, status:'all', search:undefined, category_id:undefined }];
  qc.setQueryData(key, { items: [product], meta: { pagination: { page:1, size:25, total:1, page_count:1 }, filters: { status:'all' }, expansions: [] } });
  return key;
}

const factory = () => {
  const qc = new QueryClient();
  const product = { product_id: 99, name: 'Gadget', quantity: 4, min_stock: 2, max_stock: 10, reorder_point: 3 };
  const key = seedItemsCache(qc, product);
  const Wrapper = ({ children }: any) => <ToastProvider><QueryClientProvider client={qc}>{children}</QueryClientProvider></ToastProvider>;
  return { qc, key, product, Wrapper };
};

describe('Partial threshold update', () => {
  beforeEach(() => vi.resetAllMocks());

  it('updates only provided field (minStock)', async () => {
    const { Wrapper, qc, key, product } = factory();
    const { result } = renderHook(() => useUpdateInventoryStockSettings(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.mutateAsync({ productId: 99, minStock: 5 });
    });

    const cached = qc.getQueryData<any>(key);
    expect(cached.items[0].min_stock).toBe(5);
    expect(cached.items[0].max_stock).toBe(product.max_stock);
    expect(cached.items[0].reorder_point).toBe(product.reorder_point);
    expect(inventoryService.updateProduct).toHaveBeenCalledWith(99, { min_stock: 5 });
  });
});
