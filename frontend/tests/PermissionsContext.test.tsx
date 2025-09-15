import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { PermissionsProvider, usePermission } from '../context/PermissionsContext';

// Mock apiClient
vi.mock('../lib/api', () => ({
  apiClient: {
    get: vi.fn(async () => ({ permissions: ['products:read', 'sales:write'] })),
  }
}));

function Probe() {
  const { allowed } = usePermission('products:read');
  const { allowed: denied } = usePermission('inventory:write');
  return (
    <div>
      <span data-testid="allowed">{String(allowed)}</span>
      <span data-testid="denied">{String(denied)}</span>
    </div>
  );
}

describe('PermissionsContext', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('provides allowed/denied booleans', async () => {
    render(<PermissionsProvider><Probe /></PermissionsProvider>);
    await waitFor(() => {
      expect(screen.getByTestId('allowed').textContent).toBe('true');
    });
    expect(screen.getByTestId('denied').textContent).toBe('false');
  });
});
