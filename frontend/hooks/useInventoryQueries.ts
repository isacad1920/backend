import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryService } from '../services/inventory';
import { queryKeys } from '../lib/queryKeys';
import { mapError } from '../lib/errorMap';
import { useToast } from '../context/ToastContext';
import type { InventorySummary, UnifiedInventoryItem } from '../types';

interface AdjustStockInput { productId: number; adjustment: number; reason: string; }
interface UpdateStockSettingsInput { productId: number; minStock?: number | null; maxStock?: number | null; reorderPoint?: number | null; }

export function useAdjustInventoryStock() {
  const { push } = useToast();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ['inventory','adjust','stock'],
    mutationFn: async (input: AdjustStockInput) => {
      return inventoryService.adjustProductStock(input.productId, { productId: input.productId, adjustment: input.adjustment, reason: input.reason });
    },
    onMutate: async (vars) => {
      const { productId, adjustment } = vars;
      // cancel relevant queries
      const itemsKeyPrefix = ['inventory','items'];
      const summaryKey = queryKeys.inventorySummary();
      await Promise.all([
        queryClient.cancelQueries({ queryKey: itemsKeyPrefix }),
        queryClient.cancelQueries({ queryKey: summaryKey }),
        queryClient.cancelQueries({ queryKey: queryKeys.inventoryValuation() })
      ]);

      // snapshot previous
      const prevItemsCache = queryClient.getQueriesData<any>({ queryKey: itemsKeyPrefix });
      const prevSummary = queryClient.getQueryData(summaryKey);
      const prevValuation = queryClient.getQueryData(queryKeys.inventoryValuation());

      // optimistic update over every items query result
      prevItemsCache.forEach(([key, data]) => {
        if (!data || !data.items) return;
        const updated = {
          ...data,
          items: data.items.map((it: UnifiedInventoryItem) => (it.product_id === productId ? { ...it, quantity: (it.quantity ?? 0) + adjustment } : it))
        };
        queryClient.setQueryData(key as any, updated);
      });
      if (prevSummary && (prevSummary as any).total_quantity !== undefined) {
        queryClient.setQueryData(summaryKey, { ...prevSummary as any, total_quantity: (prevSummary as any).total_quantity + adjustment });
      }
      // return context for rollback
      return { prevItemsCache, prevSummary, prevValuation };
    },
    onError: (err, _vars, ctx) => {
      // rollback
      if (ctx?.prevItemsCache) {
        ctx.prevItemsCache.forEach(([key, data]: any) => {
          queryClient.setQueryData(key, data);
        });
      }
      if (ctx?.prevSummary) queryClient.setQueryData(queryKeys.inventorySummary(), ctx.prevSummary);
      if (ctx?.prevValuation) queryClient.setQueryData(queryKeys.inventoryValuation(), ctx.prevValuation);
      const mapped = mapError(err);
      push({ type: 'error', title: 'Adjustment Failed', message: mapped.uiMessage });
    },
    onSuccess: (_data, vars) => {
      push({ type: 'success', title: 'Stock Adjusted', message: `Product #${vars.productId} adjusted by ${vars.adjustment}` });
    },
    onSettled: () => {
      // refetch summary & valuation for accuracy
      queryClient.invalidateQueries({ queryKey: queryKeys.inventorySummary() });
      queryClient.invalidateQueries({ queryKey: queryKeys.inventoryValuation() });
    }
  });
}

export function useUpdateInventoryStockSettings() {
  const { push } = useToast();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ['inventory','update','stockSettings'],
    mutationFn: async (input: UpdateStockSettingsInput) => {
      const { productId, minStock, maxStock, reorderPoint } = input;
      // Backend currently uses product update; map fields to expected property names if unified endpoint differs later
      return inventoryService.updateProduct(productId, {
        min_stock: minStock ?? undefined,
        max_stock: maxStock ?? undefined,
        reorder_point: reorderPoint ?? undefined
      } as any);
    },
    onMutate: async (vars) => {
      const { productId, minStock, maxStock, reorderPoint } = vars;
      const itemsKeyPrefix = ['inventory','items'];
      await queryClient.cancelQueries({ queryKey: itemsKeyPrefix });
      const prevItemsCache = queryClient.getQueriesData<any>({ queryKey: itemsKeyPrefix });
      prevItemsCache.forEach(([key, data]) => {
        if (!data?.items) return;
        const updated = {
          ...data,
            items: data.items.map((it: UnifiedInventoryItem) => it.product_id === productId ? {
              ...it,
              // optimistic placeholders (even if backend uses different field names)
              min_stock: minStock ?? (it as any).min_stock,
              max_stock: maxStock ?? (it as any).max_stock,
              reorder_point: reorderPoint ?? (it as any).reorder_point
            } : it)
        };
        queryClient.setQueryData(key as any, updated);
      });
      return { prevItemsCache };
    },
    onError: (err, _vars, ctx) => {
      if (ctx?.prevItemsCache) {
        ctx.prevItemsCache.forEach(([key, data]: any) => queryClient.setQueryData(key, data));
      }
      const mapped = mapError(err);
      push({ type: 'error', title: 'Update Failed', message: mapped.uiMessage });
    },
    onSuccess: (_data, vars) => {
      push({ type: 'success', title: 'Stock Settings Updated', message: `Product #${vars.productId} thresholds saved.` });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory','items'] });
    }
  });
}

interface ItemsParams { page?: number; size?: number; search?: string; status?: 'all' | 'low_stock' | 'dead_stock'; category_id?: number; }

export function useInventoryItems(params: ItemsParams, opts?: { enabled?: boolean }) {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventoryItems(params),
    enabled: opts?.enabled !== false,
    placeholderData: (prev) => prev,
    queryFn: async () => {
      try {
        const { items, meta } = await inventoryService.getItems({
          page: params.page,
          size: params.size,
          search: params.search,
          status: params.status,
          category_id: params.category_id
        });
        return { items, meta };
      } catch (e) {
        const mapped = mapError(e);
        push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Inventory Load Failed', message: mapped.uiMessage });
        throw e;
      }
    }
  });
}

export function useInventoryLowBatch(params: { page?: number; page_size?: number; threshold?: number; search?: string; category_id?: number }) {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventoryLowBatch(params),
    placeholderData: (prev) => prev,
    queryFn: async () => {
      try { return await inventoryService.getLowStockBatch(params); } catch (e) { const mapped = mapError(e); push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Low Stock Failed', message: mapped.uiMessage }); throw e; }
    }
  });
}

export function useInventoryDead(params: ItemsParams) {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventoryDead(params),
    placeholderData: (prev) => prev,
    queryFn: async () => {
      try { return await inventoryService.getDeadStock({ page: params.page, size: params.size, search: params.search, category_id: params.category_id }); } catch (e) { const mapped = mapError(e); push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Dead Stock Failed', message: mapped.uiMessage }); throw e; }
    }
  });
}

export function useInventoryMovements(params: { page?: number; size?: number; productId?: number }) {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventoryMovements(params),
    placeholderData: (prev) => prev,
    queryFn: async () => {
      try { return await inventoryService.getMovements(params); } catch (e) { const mapped = mapError(e); push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Movements Failed', message: mapped.uiMessage }); throw e; }
    }
  });
}

export function useInventorySummary() {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventorySummary(),
    staleTime: 30_000,
    queryFn: async () => {
      try { return await inventoryService.getSummary(); } catch (e) { const mapped = mapError(e); push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Summary Failed', message: mapped.uiMessage }); throw e; }
    }
  });
}

export function useInventoryValuation() {
  const { push } = useToast();
  return useQuery({
    queryKey: queryKeys.inventoryValuation(),
    staleTime: 60_000,
    queryFn: async () => {
      try { return await inventoryService.getValuation(); } catch (e) { const mapped = mapError(e); push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Valuation Failed', message: mapped.uiMessage }); throw e; }
    }
  });
}
