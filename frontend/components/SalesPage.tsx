import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Plus, Search, Download, Eye, Edit, DollarSign, ShoppingCart, TrendingUp, Calendar, Loader2, Filter, RefreshCw } from 'lucide-react';
import { salesService } from '../services/sales';
import type { Sale, SaleStatus } from '../types';
import { useAuth, PermissionGuard } from '../context/AuthContext';

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
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <PermissionGuard anyOf={['sales:update']} fallback={null}>
                              <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                                <Edit className="w-4 h-4" />
                              </Button>
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
    </div>
  );
}