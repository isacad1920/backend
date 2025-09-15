import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { PermissionsProvider, Permission, usePermission } from '../context/PermissionsContext';

// Mock apiClient to return fixed permissions
vi.mock('../lib/api', () => ({
  apiClient: {
    get: vi.fn(async () => ({ permissions: ['products:read', 'products:write', 'sales:read'] })),
  }
}));

function MultiProbe() {
  const { allowed: allAllowed } = usePermission(['products:read', 'products:write']);
  const { allowed: anyAllowed } = usePermission(['inventory:read', 'products:write'], { any: true });
  const { allowed: none } = usePermission(['users:delete']);
  return (
    <div>
      <span data-testid="all">{String(allAllowed)}</span>
      <span data-testid="any">{String(anyAllowed)}</span>
      <span data-testid="none">{String(none)}</span>
      <Permission perm="products:write"><div data-testid="perm-child">VISIBLE</div></Permission>
      <Permission perm="users:delete" fallback={<div data-testid="fallback">FALLBACK</div>}><div>SHOULD-NOT-SEE</div></Permission>
    </div>
  );
}

describe('Permission component integration', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('evaluates any/all logic and renders fallback', async () => {
    render(<PermissionsProvider><MultiProbe /></PermissionsProvider>);
    await waitFor(() => {
      expect(screen.getByTestId('all').textContent).toBe('true');
    });
    expect(screen.getByTestId('any').textContent).toBe('true');
    expect(screen.getByTestId('none').textContent).toBe('false');
    expect(screen.getByTestId('perm-child').textContent).toBe('VISIBLE');
    expect(screen.getByTestId('fallback').textContent).toBe('FALLBACK');
  });
});
