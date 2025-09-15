import { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface SyncConfig<T extends Record<string, any>> {
  state: T;
  /** keys that should sync with URL */
  keys: (keyof T)[];
  /** prefix for param names (optional) */
  prefix?: string;
  /** mapping to transform value before writing */
  encode?: (key: keyof T, value: any) => string | undefined;
  /** mapping to transform value when reading */
  decode?: (key: keyof T, value: string) => any;
  replace?: boolean; // use history.replaceState instead of push
}

/**
 * Keeps specified state keys in sync with URL query parameters.
 * One-way: state -> URL (on change). For initial load, you can hydrate
 * before calling by reading search params manually if desired.
 */
export function useUrlQuerySync<T extends Record<string, any>>(config: SyncConfig<T>) {
  const { state, keys, prefix = '', encode, decode, replace } = config;
  const location = useLocation();
  const navigate = useNavigate();
  const lastParamsRef = useRef<string>('');

  // On state change, sync to URL (shallow compare to avoid loops)
  useEffect(() => {
    const url = new URL(window.location.href);
    let changed = false;
    keys.forEach(k => {
      const raw = state[k];
      const paramName = `${prefix}${String(k)}`;
      const encoded = encode ? encode(k, raw) : raw == null || raw === '' ? undefined : String(raw);
      const current = url.searchParams.get(paramName);
      if (encoded === undefined) {
        if (current !== null) { url.searchParams.delete(paramName); changed = true; }
      } else if (current !== encoded) {
        url.searchParams.set(paramName, encoded);
        changed = true;
      }
    });
    const newQuery = url.searchParams.toString();
    if (changed && newQuery !== lastParamsRef.current) {
      lastParamsRef.current = newQuery;
      navigate(`${location.pathname}?${newQuery}`, { replace });
    }
  }, [state, keys, prefix, encode, navigate, location.pathname, replace]);

  // TODO (future): optional two-way sync (URL -> state) if needed.
}
