import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { SalesPage } from '../components/SalesPage';

vi.mock('../context/ToastContext', () => ({ useToast: () => ({ push: () => {} }) }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ hasPermission: () => true }), PermissionGuard: ({ children }: any) => <>{children}</> }));

const mockGetSales = vi.fn().mockResolvedValue({
  items: [
    {
      id: 10,
      saleNumber: 'S-001',
      branchId: 1,
      userId: 1,
      totalAmount: '100',
      paidAmount: '40',
      dueAmount: '60',
      discount: '0',
      status: 'COMPLETED',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      items: [
        { id: 501, saleId: 10, productId: 1, quantity: 2, unitPrice: '20', discount: '0', totalPrice: '40' },
        { id: 502, saleId: 10, productId: 2, quantity: 3, unitPrice: '20', discount: '0', totalPrice: '60' }
      ],
      payments: []
    }
  ],
  pagination: { page: 1, size: 10, total: 1 }
});
const mockAddPayment = vi.fn().mockResolvedValue({ success: true, payment: { id: 1, saleId: 10, accountId: 1, amount: '10', method: 'CASH', currency: 'USD', createdAt: new Date().toISOString() }, remainingBalance: '50' });
const mockCreateSaleReturn = vi.fn().mockResolvedValue({ success: true, return: { id: 77, saleId: 10, items: [], type: 'REFUND_ONLY', reason: 'Test', totalRefund: '20', createdAt: new Date().toISOString() } });

vi.mock('../services/sales', () => ({
  salesService: {
    getSales: (...args: any[]) => mockGetSales(...args),
    addPaymentToSale: (...args: any[]) => mockAddPayment(...args),
    createSaleReturn: (...args: any[]) => mockCreateSaleReturn(...args)
  }
}));

vi.mock('../services/accounts', () => ({
  accountsService: {
    getAccounts: () => Promise.resolve({ items: [{ id: 1, name: 'Cash USD', type: 'CASH_US', currency: 'USD', balance: '1000', isActive: true, createdAt: '', updatedAt: '' }], pagination: { page:1, size: 50, total: 1 } })
  }
}));

describe('SalesPage payments & returns', () => {
  beforeEach(() => { mockGetSales.mockClear(); mockAddPayment.mockClear(); mockCreateSaleReturn.mockClear(); });

  it('opens payment modal and submits payment', async () => {
    render(<SalesPage />);
    await waitFor(() => expect(mockGetSales).toHaveBeenCalled());
  const payBtn = await screen.findByRole('button', { name: /Add Payment for S-001/i });
    fireEvent.click(payBtn);
  // Assert modal heading (avoid ambiguity with submit button text)
  expect(await screen.findByRole('heading', { name: /Add Payment/i })).toBeInTheDocument();
  // account auto-selected (single account) by component logic
    const amountInput = screen.getByPlaceholderText('0.00');
    fireEvent.change(amountInput, { target: { value: '10' } });
  const submit = screen.getByTestId('submit-payment');
    fireEvent.click(submit);
    await waitFor(() => expect(mockAddPayment).toHaveBeenCalled());
  });

  it('opens return modal and processes return', async () => {
    render(<SalesPage />);
    await waitFor(() => expect(mockGetSales).toHaveBeenCalled());
    // Return button has text 'R'
  const returnBtn = await screen.findByRole('button', { name: /Return Sale S-001/i });
    fireEvent.click(returnBtn);
  expect(await screen.findByRole('heading', { name: /Return - #S-001/i })).toBeInTheDocument();
    // set a quantity on first item
    const qtyInputs = screen.getAllByRole('spinbutton');
    fireEvent.change(qtyInputs[0], { target: { value: '1' } });
    const processBtn = screen.getByRole('button', { name: /Process Return/i });
    fireEvent.click(processBtn);
    await waitFor(() => expect(mockCreateSaleReturn).toHaveBeenCalled());
  });
});
