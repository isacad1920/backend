// Generic Result<T> utility to standardize success/error handling in services
// Mirrors common functional style (Ok/Err) while remaining lightweight.

export type Result<T, E = string> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

export function err<E = string>(error: E): Result<never, E> {
  return { ok: false, error };
}

export async function toResult<T>(p: Promise<T>): Promise<Result<T>> {
  try {
    const value = await p;
    return ok(value);
  } catch (e) {
    const message = e instanceof Error ? e.message : 'Unknown error';
    return err(message);
  }
}

// Helper to unwrap (throws if error) for ergonomic transitional adoption
export function unwrap<T, E>(r: Result<T, E>): T {
  if (!r.ok) throw new Error(String(r.error));
  return r.value;
}