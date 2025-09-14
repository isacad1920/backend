import { useRef, useState, useCallback } from 'react';

export interface OptimisticItem<T> {
  data: T;
  optimistic?: boolean;
  tempId?: number;
}

type Updater<T> = (items: T[]) => T[];

interface UseOptimisticListOptions<T> {
  findId: (item: T) => string | number;
}

export function useOptimisticList<T>(initial: T[] = [], options: UseOptimisticListOptions<T>) {
  const { findId } = options;
  const [items, setItems] = useState<T[]>(initial);
  const rollbackStack = useRef<T[][]>([]);

  const snapshot = () => { rollbackStack.current.push([...items]); };

  const rollback = useCallback(() => {
    const prev = rollbackStack.current.pop();
    if (prev) setItems(prev);
  }, []);

  const commit = useCallback(() => {
    rollbackStack.current = [];
  }, []);

  const addOptimistic = useCallback((item: T) => {
    snapshot();
    setItems(prev => [item, ...prev]);
  }, [snapshot]);

  const updateOptimistic = useCallback((id: string | number, patch: Partial<T>) => {
    snapshot();
    setItems(prev => prev.map(i => findId(i) === id ? { ...i, ...patch } : i));
  }, [snapshot, findId]);

  const replaceId = useCallback((tempId: string | number, real: T) => {
    setItems(prev => prev.map(i => findId(i) === tempId ? real : i));
  }, [findId]);

  const removeOptimistic = useCallback((id: string | number) => {
    snapshot();
    setItems(prev => prev.filter(i => findId(i) !== id));
  }, [snapshot, findId]);

  return {
    items,
    setItems,
    addOptimistic,
    updateOptimistic,
    replaceId,
    removeOptimistic,
    rollback,
    commit,
  };
}
