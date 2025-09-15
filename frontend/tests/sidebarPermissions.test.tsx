import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';

// --- Dynamic mock state for permissions context ---
interface MockState {
  permissions: string[];
  loading: boolean;
}

const mockState: MockState = { permissions: [], loading: false };

// Helper to compute has() consistent with real context implementation
function has(perm: string | string[], permissions: string[], opts?: { any?: boolean }) {
  const list = Array.isArray(perm) ? perm : [perm];
  if (permissions.includes('all')) return true;
  return opts?.any ? list.some(p => permissions.includes(p)) : list.every(p => permissions.includes(p));
}

vi.mock('../context/PermissionsContext', () => ({
  usePermissions: () => ({
    permissions: mockState.permissions,
    loading: mockState.loading,
    refresh: async () => {},
    has: (perm: string | string[], opts?: { any?: boolean }) => has(perm, mockState.permissions, opts)
  })
}));

function renderSidebar() {
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Sidebar user={{ name: 'Test User', role: 'user' }} onLogout={() => {}} />
    </MemoryRouter>
  );
}

const ALL_LABELS = [
  'Dashboard',
  'Point of Sale',
  'Sales',
  'Inventory',
  'Products',
  'Customers',
  'Branches',
  'Categories',
  'Users & Permissions',
  'Journal & Accounting',
  'Notifications',
  'Reports',
  'Audit Logs',
  'Backup & Restore',
  'System Settings'
];

describe('Sidebar permission display logic', () => {
  beforeEach(() => {
    mockState.permissions = [];
    mockState.loading = false;
  });

  it('shows all pages while permissions loading (permissive mode)', () => {
    mockState.loading = true;
    renderSidebar();
    for (const label of ALL_LABELS) {
      expect(screen.getByRole('button', { name: new RegExp(label, 'i') })).toBeInTheDocument();
    }
  });

  it('shows all pages when permissions empty', () => {
    renderSidebar();
    for (const label of ALL_LABELS) {
      expect(screen.getByRole('button', { name: new RegExp(label, 'i') })).toBeInTheDocument();
    }
  });

  it('shows all pages when small permission set (<=3) triggers fallback', () => {
    mockState.permissions = ['sales:view'];
    renderSidebar();
    expect(screen.getByRole('button', { name: /Audit Logs/i })).toBeInTheDocument(); // would normally require audit:view
    expect(screen.getByRole('button', { name: /System Settings/i })).toBeInTheDocument();
  });

  it('filters pages once sufficient permission list (>3) provided', () => {
    mockState.permissions = ['sales:view','inventory:view','customers:view','products:view']; // length 4 -> filtering mode
    renderSidebar();
    // Visible ones
    expect(screen.getByRole('button', { name: /Sales/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Inventory/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Products/i })).toBeInTheDocument();
    // Hidden ones requiring permissions not present
    expect(screen.queryByRole('button', { name: /Audit Logs/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /System Settings/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Backup & Restore/i })).not.toBeInTheDocument();
  });

  it('shows all pages for admin via all code', () => {
    mockState.permissions = ['all'];
    renderSidebar();
    for (const label of ALL_LABELS) {
      expect(screen.getByRole('button', { name: new RegExp(label, 'i') })).toBeInTheDocument();
    }
  });
});
