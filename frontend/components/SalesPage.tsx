import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Plus, Search, Download, Eye, Edit, DollarSign, ShoppingCart, TrendingUp, Calendar, Loader2, Filter, RefreshCw, CreditCard, Banknote } from 'lucide-react';
import type { Sale, SaleStatus, PaymentMethod, Account, Currency } from '../types';
import { salesService } from '../services/sales';
import { useAuth, PermissionGuard } from '../context/AuthContext';
import { accountsService } from '../services/accounts';
import { useToast } from '../context/ToastContext';

interface EnrichedSale extends Sale {
  // placeholders for analytics until backend endpoints exist
  itemsCount?: number;
  paymentMethodSummary?: string;
}

export function SalesPage() {
  const { hasPermission } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [sales, setSales] = useState<EnrichedSale[]>([]);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('sales');
  // Payment modal state
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [paymentSale, setPaymentSale] = useState<EnrichedSale | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [paymentAccountId, setPaymentAccountId] = useState<number | ''>('');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('CASH' as PaymentMethod);
  const [paymentCurrency, setPaymentCurrency] = useState<Currency | ''>('');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentReference, setPaymentReference] = useState('');
  const [paymentSubmitting, setPaymentSubmitting] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const { push } = useToast();
  // Return / refund modal state
  const [returnOpen, setReturnOpen] = useState(false);
  const [returnSale, setReturnSale] = useState<EnrichedSale | null>(null);
  const [returnItems, setReturnItems] = useState<Array<{ saleItemId: number; quantity: number; refundAmount: string }>>([]);
  const [returnType, setReturnType] = useState<'REFUND_ONLY' | 'EXCHANGE'>('REFUND_ONLY');
  const [returnReason, setReturnReason] = useState('');
  const [returnSubmitting, setReturnSubmitting] = useState(false);
  const [returnError, setReturnError] = useState<string | null>(null);
  const debouncedFetchRef = React.useRef<number | null>(null);

  const fetchSales = useCallback(async (override?: { page?: number; size?: number; term?: string }) => {
    if (!hasPermission('sales:view')) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await salesService.getSales({
        page: override?.page ?? page,
        size: override?.size ?? size,
  q: (override?.term ?? searchTerm) || undefined,
        status: statusFilter !== 'all' ? (statusFilter as SaleStatus) : undefined,
        from: fromDate || undefined,
        to: toDate || undefined,
      });
      const enriched = (resp.items as Sale[]).map(s => ({
        ...s,
        itemsCount: s.items?.reduce((acc, it) => acc + (it.quantity || 0), 0) || undefined,
        paymentMethodSummary: s.payments && s.payments.length > 0 ? s.payments[0].paymentMethod : undefined,
      }));
      setSales(enriched);
      setTotal(resp.pagination.total);
    } catch (e: any) {
      setError(e?.message || 'Failed to load sales');
    } finally {
      setLoading(false);
    }
  }, [page, size, searchTerm, statusFilter, fromDate, toDate, hasPermission]);

  const openPayment = async (sale: EnrichedSale) => {
    setPaymentSale(sale);
    setPaymentOpen(true);
    setPaymentAmount(sale.dueAmount);
    setPaymentAccountId('');
    setPaymentCurrency('');
  setPaymentMethod('CASH' as PaymentMethod);
    setPaymentReference('');
    setPaymentError(null);
    if (!accounts.length) {
      try {
        setAccountsLoading(true);
        const resp = await accountsService.getAccounts({ size: 100 });
        setAccounts(resp.items as Account[]);
        if (resp.items && resp.items.length === 1) {
          const only = resp.items[0] as Account;
          setPaymentAccountId(only.id as number);
          setPaymentCurrency(only.currency as Currency);
        }
      } catch (err: any) {
        push({ type: 'error', title: 'Accounts Load Failed', message: err?.message || 'Unable to load accounts' });
      } finally { setAccountsLoading(false); }
    }
  };

  const handleSubmitPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paymentSale) return;
    if (!paymentAccountId) { setPaymentError('Account required'); return; }
    const amt = Number(paymentAmount);
    if (!(amt > 0)) { setPaymentError('Amount must be > 0'); return; }
    const due = Number(paymentSale.dueAmount || 0);
    if (amt > due) { setPaymentError('Amount exceeds due'); return; }
    const selectedAccount = accounts.find(a => a.id === paymentAccountId);
    const currency = paymentCurrency || selectedAccount?.currency || 'USD';
    setPaymentSubmitting(true); setPaymentError(null);
    // optimistic update
    const original = paymentSale;
    const optimisticPaid = (Number(original.paidAmount || 0) + amt).toString();
    const optimisticDue = (Number(original.totalAmount || 0) - Number(optimisticPaid)).toString();
    setSales(prev => prev.map(s => s.id === original.id ? { ...s, paidAmount: optimisticPaid, dueAmount: optimisticDue } : s));
    try {
      const resp = await salesService.addPaymentToSale(original.id, { accountId: paymentAccountId as number, amount: amt.toString(), method: paymentMethod, currency });
      // Optionally adjust due from response.remainingBalance
      if (resp?.remainingBalance !== undefined) {
        setSales(prev => prev.map(s => s.id === original.id ? { ...s, paidAmount: (Number(original.paidAmount || 0) + amt).toString(), dueAmount: resp.remainingBalance ?? '0' } : s));
      }
      push({ type: 'success', title: 'Payment Added', message: `Sale #${original.saleNumber} updated` });
      setPaymentOpen(false);
    } catch (err: any) {
      // rollback
      setSales(prev => prev.map(s => s.id === original.id ? original : s));
      setPaymentError(err?.message || 'Payment failed');
    } finally { setPaymentSubmitting(false); }
  };

  const openReturn = (sale: EnrichedSale) => {
    if (!sale.items || sale.items.length === 0) {
      push({ type: 'error', title: 'No Items', message: 'Sale has no items to return.' });
      return;
    }
    setReturnSale(sale);
    setReturnOpen(true);
    setReturnType('REFUND_ONLY');
    setReturnReason('');
    setReturnError(null);
    // Initialize with zero quantities
    setReturnItems(sale.items.map(it => ({ saleItemId: it.id, quantity: 0, refundAmount: '0' })));
  };

  const updateReturnItem = (saleItemId: number, field: 'quantity' | 'refundAmount', value: string) => {
    setReturnItems(prev => prev.map(it => it.saleItemId === saleItemId ? { ...it, [field]: field === 'quantity' ? Number(value) : value } : it));
  };

  const totalRefund = returnItems.reduce((acc, it) => acc + Number(it.refundAmount || 0), 0);

  const handleSubmitReturn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!returnSale) return;
    const anyQty = returnItems.some(it => it.quantity > 0);
    if (!anyQty) { setReturnError('Select at least one item with quantity > 0'); return; }
    setReturnSubmitting(true); setReturnError(null);
    const original = returnSale;
    // optimistic: mark status REFUNDED (if refund only) and adjust paid/due minimally; real backend may recalc.
    const optimistic = { ...original, status: returnType === 'REFUND_ONLY' ? 'REFUNDED' : original.status } as EnrichedSale;
    setSales(prev => prev.map(s => s.id === original.id ? optimistic : s));
    try {
      await salesService.createSaleReturn(original.id, {
        items: returnItems.filter(it => it.quantity > 0),
        type: returnType,
        reason: returnReason || 'Customer return'
      });
      push({ type: 'success', title: 'Return Processed', message: `Sale #${original.saleNumber} updated` });
      setReturnOpen(false);
    } catch (err: any) {
      setSales(prev => prev.map(s => s.id === original.id ? original : s));
      setReturnError(err?.message || 'Return failed');
    } finally { setReturnSubmitting(false); }
  };

  // initial load
  useEffect(() => { fetchSales(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // debounce search
  useEffect(() => {
    if (debouncedFetchRef.current) window.clearTimeout(debouncedFetchRef.current);
    debouncedFetchRef.current = window.setTimeout(() => {
      setPage(1);
      fetchSales({ page: 1 });
    }, 300);
    return () => { if (debouncedFetchRef.current) window.clearTimeout(debouncedFetchRef.current); };
  }, [searchTerm, fetchSales]);

  // refetch on filter changes (status, date range)
  useEffect(() => { setPage(1); fetchSales({ page: 1 }); }, [statusFilter, fromDate, toDate]); // eslint-disable-line react-hooks/exhaustive-deps

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'cancelled': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'draft': return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
      case 'refunded': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Sales Management</h1>
          <p className="text-white/70">Track and manage all sales transactions</p>
        </div>
        <div className="flex space-x-2">
          <PermissionGuard anyOf={['sales:create']} fallback={null}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
              <Plus className="w-4 h-4 mr-2" />
              New Sale
            </Button>
          </PermissionGuard>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI placeholders (will wire real summary endpoint later) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-white/70 text-sm">Total Revenue (page)</p>
                <p className="text-white text-xl">
                  ${sales.reduce((acc, s) => acc + Number(s.totalAmount || 0), 0).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-white/70 text-sm">Sales (page)</p>
                <p className="text-white text-xl">{sales.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-8 h-8 text-purple-400" />
              <div>
                <p className="text-white/70 text-sm">Avg Sale Value (page)</p>
                <p className="text-white text-xl">
                  {sales.length > 0 ? `$${(sales.reduce((acc, s) => acc + Number(s.totalAmount || 0), 0)/sales.length).toFixed(2)}` : '—'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-8 h-8 text-orange-400" />
              <div>
                <p className="text-white/70 text-sm">Filters Active</p>
                <p className="text-white text-xl">
                  {[statusFilter !== 'all', !!fromDate, !!toDate, !!searchTerm].filter(Boolean).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="sales" className="data-[state=active]:bg-white/20 text-white">Sales List</TabsTrigger>
          <TabsTrigger value="payments" className="data-[state=active]:bg-white/20 text-white">Payments</TabsTrigger>
          <TabsTrigger value="reports" className="data-[state=active]:bg-white/20 text-white">AR Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="sales" className="space-y-4">
          {/* Filter Bar */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4 space-y-4">
                <div className="flex flex-col md:flex-row md:items-center md:space-x-4 space-y-3 md:space-y-0">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/50 w-4 h-4" />
                    <Input
                      placeholder="Search sales (number, customer)..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    />
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-40 bg-white/10 border-white/20 text-white">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="COMPLETED">Completed</SelectItem>
                      <SelectItem value="PENDING">Pending</SelectItem>
                      <SelectItem value="DRAFT">Draft</SelectItem>
                      <SelectItem value="CANCELLED">Cancelled</SelectItem>
                      <SelectItem value="REFUNDED">Refunded</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center space-x-2 text-white/70 text-xs">
                    <div className="flex flex-col">
                      <label className="mb-1">From</label>
                      <Input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} className="bg-white/10 border-white/20 text-white" />
                    </div>
                    <div className="flex flex-col">
                      <label className="mb-1">To</label>
                      <Input type="date" value={toDate} onChange={e => setToDate(e.target.value)} className="bg-white/10 border-white/20 text-white" />
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-white/30 text-white hover:bg-white/10"
                    onClick={() => { setFromDate(''); setToDate(''); setStatusFilter('all'); setSearchTerm(''); }}
                  >
                    <Filter className="w-4 h-4 mr-1" /> Reset
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={loading}
                    className="border-white/30 text-white hover:bg-white/10"
                    onClick={() => fetchSales()}
                  >
                    <RefreshCw className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} /> Reload
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Sales Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                {error && (
                  <div className="p-4 mb-4 bg-red-500/10 border border-red-500/20 rounded text-red-300 text-sm">
                    {error} <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={() => fetchSales()}>Retry</Button>
                  </div>
                )}
                <Table>
                  <TableHeader>
                    <TableRow className="border-white/20">
                      <TableHead className="text-white/70">Sale #</TableHead>
                      <TableHead className="text-white/70">Customer</TableHead>
                      <TableHead className="text-white/70">Date</TableHead>
                      <TableHead className="text-white/70">Items</TableHead>
                      <TableHead className="text-white/70">Total</TableHead>
                      <TableHead className="text-white/70">Paid</TableHead>
                      <TableHead className="text-white/70">Due</TableHead>
                      <TableHead className="text-white/70">Status</TableHead>
                      <TableHead className="text-white/70">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading && (
                      <TableRow className="border-white/10">
                        <TableCell colSpan={9} className="py-10 text-center text-white/60">
                          <Loader2 className="w-5 h-5 mr-2 inline animate-spin" /> Loading sales...
                        </TableCell>
                      </TableRow>
                    )}
                    {!loading && sales.length === 0 && !error && (
                      <TableRow className="border-white/10">
                        <TableCell colSpan={9} className="py-10 text-center text-white/60">
                          No sales found
                        </TableCell>
                      </TableRow>
                    )}
                    {!loading && sales.map(sale => (
                      <TableRow key={sale.id} className="border-white/10 hover:bg-white/5">
                        <TableCell className="text-white text-sm">{sale.saleNumber}</TableCell>
                        <TableCell className="text-white/70 text-xs">{sale.customer?.name || '—'}</TableCell>
                        <TableCell className="text-white/70 text-xs">{new Date(sale.createdAt).toLocaleDateString()}</TableCell>
                        <TableCell className="text-white/70 text-center text-xs">{sale.itemsCount ?? (sale.items?.length || 0)}</TableCell>
                        <TableCell className="text-white text-xs">${Number(sale.totalAmount || 0).toLocaleString()}</TableCell>
                        <TableCell className="text-white/70 text-xs">${Number(sale.paidAmount || 0).toLocaleString()}</TableCell>
                        <TableCell className={`text-xs ${Number(sale.dueAmount || 0) > 0 ? 'text-yellow-400' : 'text-green-400'}`}>${Number(sale.dueAmount || 0).toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(sale.status)}>{sale.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button aria-label="View Sale" size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <PermissionGuard anyOf={['sales:update']} fallback={null}>
                              <Button aria-label="Edit Sale" size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                                <Edit className="w-4 h-4" />
                              </Button>
                            </PermissionGuard>
                            <PermissionGuard anyOf={['sales:update']} fallback={null}>
                              {Number(sale.dueAmount || 0) > 0 && (
                                <Button aria-label={`Add Payment for ${sale.saleNumber}`} size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => openPayment(sale)}>
                                  <Banknote className="w-4 h-4" />
                                </Button>
                              )}
                            </PermissionGuard>
                            <PermissionGuard anyOf={['sales:update']} fallback={null}>
                              {sale.status !== 'REFUNDED' && sale.items && sale.items.length > 0 && (
                                <Button aria-label={`Return Sale ${sale.saleNumber}`} size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => openReturn(sale)}>
                                  R
                                </Button>
                              )}
                            </PermissionGuard>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <div className="flex items-center justify-between mt-4 text-white/70 text-sm">
                  <div>
                    Page {page} of {Math.max(1, Math.ceil(total / size))} • {total} total
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={page <= 1 || loading}
                      className="border-white/30 text-white/70 hover:text-white"
                      onClick={() => { const newPage = page - 1; setPage(newPage); fetchSales({ page: newPage }); }}
                    >Prev</Button>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={page >= Math.ceil(total / size) || loading}
                      className="border-white/30 text-white/70 hover:text-white"
                      onClick={() => { const newPage = page + 1; setPage(newPage); fetchSales({ page: newPage }); }}
                    >Next</Button>
                    <select
                      value={size}
                      onChange={(e) => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); fetchSales({ page: 1, size: newSize }); }}
                      className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none"
                    >
                      {[10,25,50].map(s => <option key={s} value={s}>{s}/page</option>)}
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
        </TabsContent>

        {/* Placeholder tabs for payments & reports (to be wired later) */}
        <TabsContent value="payments" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center text-white/60 text-sm">
              Payment list integration pending future iteration.
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="reports" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center text-white/60 text-sm">
              Accounts Receivable summary & aging will be integrated after reporting endpoints.
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      {paymentOpen && paymentSale && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-md">
            <form onSubmit={handleSubmitPayment}>
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-white font-medium text-sm flex items-center gap-2"><Banknote className="w-4 h-4" /> Add Payment - #{paymentSale.saleNumber}</h2>
                <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setPaymentOpen(false)}>×</Button>
              </div>
              <div className="p-4 space-y-4">
                {paymentError && <div className="text-xs text-red-400">{paymentError}</div>}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1 col-span-2">
                    <label htmlFor="payment-account" className="text-xs text-white/70">Account *</label>
                    <select id="payment-account" aria-label="Account" value={paymentAccountId} onChange={e=> { const v = e.target.value ? Number(e.target.value) : ''; setPaymentAccountId(v as any); if (v) { const acc = accounts.find(a=>a.id===Number(v)); if (acc) setPaymentCurrency(acc.currency); } }} className="bg-white/10 border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                      <option value="">Select account</option>
                      {accountsLoading && <option>Loading...</option>}
                      {!accountsLoading && accounts.map(a => <option key={a.id} value={a.id}>{a.name} ({a.currency})</option>)}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Amount *</label>
                    <Input value={paymentAmount} onChange={e=> setPaymentAmount(e.target.value)} className="bg-white/10 border-white/20 text-white" placeholder="0.00" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Method</label>
                    <select value={paymentMethod} onChange={e=> setPaymentMethod(e.target.value as PaymentMethod)} className="bg-white/10 border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                      {['CASH','CARD','BANK_TRANSFER','MOBILE_MONEY','CREDIT'].map(m => <option key={m} value={m}>{m.replace('_',' ')}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Currency</label>
                    <Input value={paymentCurrency || ''} onChange={e=> setPaymentCurrency(e.target.value as Currency)} placeholder="Auto" className="bg-white/10 border-white/20 text-white" />
                  </div>
                  <div className="space-y-1 col-span-2">
                    <label className="text-xs text-white/70">Reference</label>
                    <Input value={paymentReference} onChange={e=> setPaymentReference(e.target.value)} className="bg-white/10 border-white/20 text-white" placeholder="Optional reference" />
                  </div>
                  <div className="col-span-2 text-xs text-white/50 space-y-1">
                    <div>Due: ${Number(paymentSale.dueAmount || 0).toLocaleString()}</div>
                    <div>Paid: ${Number(paymentSale.paidAmount || 0).toLocaleString()}</div>
                    <div>Total: ${Number(paymentSale.totalAmount || 0).toLocaleString()}</div>
                  </div>
                </div>
              </div>
              <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setPaymentOpen(false)} disabled={paymentSubmitting}>Cancel</Button>
                <Button data-testid="submit-payment" type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={paymentSubmitting}>{paymentSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Submit Payment'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
      {returnOpen && returnSale && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-2xl max-h-full overflow-auto">
            <form onSubmit={handleSubmitReturn}>
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-white font-medium text-sm">Return - #{returnSale.saleNumber}</h2>
                <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setReturnOpen(false)}>×</Button>
              </div>
              <div className="p-4 space-y-4">
                {returnError && <div className="text-xs text-red-400">{returnError}</div>}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Type</label>
                    <select value={returnType} onChange={e=> setReturnType(e.target.value as any)} className="bg-white/10 border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                      <option value="REFUND_ONLY">Refund Only</option>
                      <option value="EXCHANGE">Exchange</option>
                    </select>
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <label className="text-xs text-white/70">Reason</label>
                    <Input value={returnReason} onChange={e=> setReturnReason(e.target.value)} className="bg-white/10 border-white/20 text-white" placeholder="Reason for return" />
                  </div>
                </div>
                <div className="border border-white/10 rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-white/10">
                        <TableHead className="text-white/70 text-xs">Item</TableHead>
                        <TableHead className="text-white/70 text-xs">Sold Qty</TableHead>
                        <TableHead className="text-white/70 text-xs">Return Qty</TableHead>
                        <TableHead className="text-white/70 text-xs">Refund/Unit</TableHead>
                        <TableHead className="text-white/70 text-xs">Line Refund</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {returnSale.items?.map(it => {
                        const ret = returnItems.find(r => r.saleItemId === it.id)!;
                        const maxQty = it.quantity;
                        const unitPrice = Number(it.unitPrice || 0);
                        const lineRefund = (ret.quantity * unitPrice).toFixed(2);
                        if (ret.refundAmount !== lineRefund) {
                          // sync refund amount automatically with quantity * unit price
                          ret.refundAmount = lineRefund;
                        }
                        return (
                          <TableRow key={it.id} className="border-white/10">
                            <TableCell className="text-white/70 text-xs">{it.product?.name || it.productId}</TableCell>
                            <TableCell className="text-white/50 text-center text-xs">{maxQty}</TableCell>
                            <TableCell className="text-white/70 text-xs">
                              <Input type="number" min={0} max={maxQty} value={ret.quantity} onChange={e => updateReturnItem(it.id, 'quantity', e.target.value)} className="bg-white/10 border-white/20 text-white h-8 w-20" />
                            </TableCell>
                            <TableCell className="text-white/50 text-xs">${unitPrice.toFixed(2)}</TableCell>
                            <TableCell className="text-white text-xs">${lineRefund}</TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
                <div className="flex justify-between items-center text-sm text-white/70">
                  <span>Total Refund</span>
                  <span className="text-white font-medium">${totalRefund.toFixed(2)}</span>
                </div>
              </div>
              <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setReturnOpen(false)} disabled={returnSubmitting}>Cancel</Button>
                <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={returnSubmitting}>{returnSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Process Return'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}