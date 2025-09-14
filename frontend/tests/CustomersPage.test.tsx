import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { CustomersPage } from '../components/CustomersPage';

// Mock contexts
vi.mock('../context/ToastContext', () => ({ useToast: () => ({ push: () => {} }) }));
vi.mock('../components/ConfirmDialog', () => ({ useConfirm: () => ({ confirm: async () => true, dialog: null }) }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ hasPermission: () => true }), PermissionGuard: ({ children }: any) => <>{children}</> }));

const mockGetCustomers = vi.fn().mockResolvedValue({
  items: [
    { id: 1, customerNumber: 'CUST-1', name: 'Alice', isActive: true, status: 'ACTIVE', type: 'INDIVIDUAL', creditLimit: '0', currency: 'USD', createdAt: '', updatedAt: '' },
    { id: 2, customerNumber: 'CUST-2', name: 'Bob', isActive: true, status: 'ACTIVE', type: 'COMPANY', creditLimit: '0', currency: 'USD', createdAt: '', updatedAt: '' }
  ],
  pagination: { page: 1, size: 10, total: 2 }
});

const mockCreateCustomer = vi.fn().mockImplementation(async (data) => ({ id: 99, ...data, isActive: true, createdAt: '', updatedAt: '' }));

vi.mock('../services/customers', () => ({
  customerService: {
    getCustomers: (...args: any[]) => mockGetCustomers(...args),
    createCustomer: (...args: any[]) => mockCreateCustomer(...args),
    updateCustomer: vi.fn(),
    deleteCustomer: vi.fn(),
    getCustomerBalance: vi.fn().mockResolvedValue({ balance: '0' })
  }
}));

describe('CustomersPage', () => {
  beforeEach(() => { mockGetCustomers.mockClear(); mockCreateCustomer.mockClear(); });

  it('renders and fetches customers list', async () => {
    render(<CustomersPage />);
    await waitFor(() => expect(mockGetCustomers).toHaveBeenCalled());
    expect(await screen.findByText('Alice')).toBeInTheDocument();
    expect(await screen.findByText('Bob')).toBeInTheDocument();
  });

  it('opens create modal and creates customer optimistically', async () => {
    render(<CustomersPage />);
    await waitFor(() => expect(mockGetCustomers).toHaveBeenCalled());

    const addBtn = await screen.findByText(/Add Customer/i);
    fireEvent.click(addBtn);
    expect(await screen.findByText(/Create Customer/i)).toBeInTheDocument();

    const nameInput = screen.getByPlaceholderText('Customer name');
    fireEvent.change(nameInput, { target: { value: 'Charlie' }});

    const createButton = screen.getByRole('button', { name: /Create$/ });
    fireEvent.click(createButton);

    // Optimistic presence
    await screen.findAllByText('Charlie');
    await waitFor(() => expect(mockCreateCustomer).toHaveBeenCalled());
  });
});
