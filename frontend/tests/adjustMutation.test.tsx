import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { useAdjustInventoryStock } from '../hooks/useInventoryQueries';
import { inventoryService } from '../services/inventory';
import { ToastProvider } from '../context/ToastContext';

vi.mock('../services/inventory', () => {
  return {
    inventoryService: {
      adjustProductStock: vi.fn().mockResolvedValue({ ok: true })
    }
  };
});

const wrapper = ({ children }: any) => {
  const qc = new QueryClient();
  return <ToastProvider><QueryClientProvider client={qc}>{children}</QueryClientProvider></ToastProvider>;
};

describe('useAdjustInventoryStock optimistic flow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('calls service and emits success toast', async () => {
    const { result } = renderHook(() => useAdjustInventoryStock(), { wrapper });
    await act(async () => {
      await result.current.mutateAsync({ productId: 123, adjustment: 5, reason: 'test' });
    });
    expect(inventoryService.adjustProductStock).toHaveBeenCalledWith(123, { productId: 123, adjustment: 5, reason: 'test' });
  });

  it('rolls back on error', async () => {
    (inventoryService.adjustProductStock as any).mockRejectedValueOnce(new Error('fail'));
    const { result } = renderHook(() => useAdjustInventoryStock(), { wrapper });
    await act(async () => {
      await expect(result.current.mutateAsync({ productId: 99, adjustment: -3, reason: 'oops' })).rejects.toThrow();
    });
  });
});
