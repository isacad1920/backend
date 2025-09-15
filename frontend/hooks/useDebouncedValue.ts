import { useEffect, useRef, useState } from 'react';

/**
 * Debounce any primitive value. Returns the debounced value that updates
 * only after delay ms of no changes.
 */
export function useDebouncedValue<T>(value: T, delay: number = 300): T {
  const [debounced, setDebounced] = useState(value);
  const timer = useRef<number | null>(null);
  useEffect(() => {
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setDebounced(value), delay);
    return () => { if (timer.current) window.clearTimeout(timer.current); };
  }, [value, delay]);
  return debounced;
}
