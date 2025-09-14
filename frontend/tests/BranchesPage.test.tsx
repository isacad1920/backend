import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BranchesPage } from '../components/BranchesPage';

// Minimal mocks for context hooks used inside BranchesPage
vi.mock('../context/ToastContext', () => ({ useToast: () => ({ push: () => {} }) }));
vi.mock('../components/ConfirmDialog', () => ({ useConfirm: () => ({ confirm: async () => true, dialog: null }) }));

const mockGetBranches = vi.fn().mockResolvedValue({
  items: [
    { id: 1, name: 'Main Branch', isActive: true, status: 'ACTIVE', createdAt: '', updatedAt: '' },
    { id: 2, name: 'East Branch', isActive: true, status: 'ACTIVE', createdAt: '', updatedAt: '' }
  ],
  pagination: { page: 1, size: 25, total: 2 }
});

vi.mock('../services/branches', () => ({
  branchesService: {
    getBranches: (...args: any[]) => mockGetBranches(...args),
    getBranchPerformance: () => Promise.resolve({ sales: '10', revenue: '1000', topProducts: [] })
  }
}));

describe('BranchesPage', () => {
  beforeEach(() => { mockGetBranches.mockClear(); });

  it('renders and fetches branches list', async () => {
    render(<BranchesPage />);
    // loading state
    expect(screen.getByText(/Loading branches/i)).toBeInTheDocument();
    await waitFor(() => expect(mockGetBranches).toHaveBeenCalled());
    const mainMatches = await screen.findAllByText('Main Branch');
    expect(mainMatches.length).toBeGreaterThan(0);
    const eastMatches = await screen.findAllByText('East Branch');
    expect(eastMatches.length).toBeGreaterThan(0);
  });
});
