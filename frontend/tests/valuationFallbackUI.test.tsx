import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook } from '@testing-library/react';
import { useInventoryValuation } from '../hooks/useInventoryQueries';

// We'll mock the service layer used by the valuation hook indirectly; simplest is to mock the hook's internal service imports.
vi.mock('../services/inventory', () => ({
  inventoryService: {
    getValuation: vi.fn().mockRejectedValue(new Error('primary valuation failed')),
    getSummary: vi.fn().mockResolvedValue({
      total_cost_value: 1000,
      total_retail_value: 1500,
      total_quantity: 50
    })
  }
}));

function wrapperFactory() {
  const qc = new QueryClient();
  const Wrapper = ({ children }: any) => <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  return { Wrapper };
}

describe('Valuation fallback hook behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('provides derived flag and summary-based valuation when primary fails', async () => {
    const { Wrapper } = wrapperFactory();
    const { result } = renderHook(() => useInventoryValuation(), { wrapper: Wrapper });

    await new Promise(r => setTimeout(r, 0)); // flush microtasks

    expect(result.current.data).toBeDefined();
    expect(result.current.data?.valuationDerived).toBe(true);
    expect(result.current.data?.total_inventory_cost).toBe(1000);
    expect(result.current.data?.total_inventory_retail).toBe(1500);
  });
});
