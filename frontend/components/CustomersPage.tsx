import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Plus, Search, Users, DollarSign, ShoppingCart, Calendar, Eye, Edit, Mail, Phone, Loader2, Trash2, AlertTriangle } from 'lucide-react';
import { customerService } from '../services/customers';
import type { Customer, CreateCustomerRequest, CustomerType, CustomerStatus } from '../types';
import { Currency, CustomerType as CTEnum } from '../types';
import { useAuth } from '../context/AuthContext';
import { PermissionGuard } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useConfirm } from './ConfirmDialog';

interface EnrichedCustomer extends Customer {
  // Backend may not provide these analytics yet; placeholders until endpoints exist
  totalSpent?: number;
  orders?: number;
  lastOrder?: string;
  arBalance?: number;
  tagStatus?: string; // derived status label
}

export function CustomersPage() {
  const { hasPermission } = useAuth();
  const { push } = useToast();
  const { confirm, dialog: confirmDialog } = useConfirm();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState<'all' | CustomerType>('all');
  const [selectedCustomer, setSelectedCustomer] = useState<EnrichedCustomer | null>(null);
  const [customers, setCustomers] = useState<EnrichedCustomer[]>([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [deleteSubmitting, setDeleteSubmitting] = useState<number | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const [newCustomer, setNewCustomer] = useState<CreateCustomerRequest>({ customerNumber: '', name: '', type: CTEnum.INDIVIDUAL, creditLimit: '0', currency: Currency.USD });
  const [editDraft, setEditDraft] = useState<Partial<Customer> | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [balanceLoadingId, setBalanceLoadingId] = useState<number | null>(null);
  const balanceLoadedRef = React.useRef<Set<number>>(new Set());

  const debouncedFetchRef = React.useRef<number | null>(null);

  const fetchCustomers = useCallback(async (override?: { page?: number; size?: number; term?: string }) => {
    if (!hasPermission('customers:view')) return;
    setLoading(true);
    setError(null);
    try {
      const searchVal = override?.term ?? searchTerm;
      const resp = await customerService.getCustomers({
        page: override?.page ?? page,
        size: override?.size ?? size,
        q: (searchVal ? searchVal : undefined),
        type: typeFilter === 'all' ? undefined : typeFilter,
        status: statusFilter === 'all' ? undefined : statusFilter.toUpperCase() as CustomerStatus
      });
      setCustomers(resp.items as EnrichedCustomer[]);
      setTotal(resp.pagination.total);
    } catch (e: any) {
      setError(e?.message || 'Failed to load customers');
    } finally {
      setLoading(false);
    }
  }, [page, size, searchTerm, hasPermission, typeFilter, statusFilter]);

  // Initial load
  useEffect(() => { fetchCustomers(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Debounce search term changes
  useEffect(() => {
    if (debouncedFetchRef.current) window.clearTimeout(debouncedFetchRef.current);
    debouncedFetchRef.current = window.setTimeout(() => {
      fetchCustomers({ page: 1 });
      setPage(1);
    }, 300);
    return () => { if (debouncedFetchRef.current) window.clearTimeout(debouncedFetchRef.current); };
  }, [searchTerm, fetchCustomers]);

  const filteredCustomers = customers; // server side filters now include status/type

  // Fetch customer balance when a customer is selected and balance not yet loaded
  useEffect(() => {
    const target = selectedCustomer;
    if (!target) return;
    if (target.balance !== undefined) return; // already has balance
    if (balanceLoadedRef.current.has(target.id)) return; // fetched before this session
    (async () => {
      try {
        setBalanceLoadingId(target.id);
        const { balance } = await customerService.getCustomerBalance(target.id);
        balanceLoadedRef.current.add(target.id);
        setCustomers(prev => prev.map(c => c.id === target.id ? { ...c, balance } as any : c));
        setSelectedCustomer(prev => (prev && prev.id === target.id) ? { ...prev, balance } as any : prev);
      } catch (err) {
        // silent fail; could add toast if desired
      } finally {
        setBalanceLoadingId(null);
      }
    })();
  }, [selectedCustomer]);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'vip': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'inactive': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getInitials = (name: string): string => {
    return name.split(' ').map((n: string) => n[0]).join('').toUpperCase();
  };

  const startCreate = () => { setNewCustomer({ customerNumber: `CUST-${Date.now()}`, name: '', type: CTEnum.INDIVIDUAL, creditLimit: '0', currency: Currency.USD }); setCreateError(null); setCreateOpen(true); };
  const startEdit = (c: EnrichedCustomer) => { setSelectedCustomer(c); setEditDraft({ name: c.name, email: c.email, phone: (c as any).phone, address: c.address, type: c.type, creditLimit: c.creditLimit, currency: c.currency, isActive: c.isActive }); setEditError(null); setEditOpen(true); };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault(); if (!newCustomer.name.trim()) { setCreateError('Name required'); return; }
    setCreateSubmitting(true); setCreateError(null);
  const optimistic: EnrichedCustomer = { id: Date.now()*-1, customerNumber: newCustomer.customerNumber || `CUST-${Date.now()}`, name: newCustomer.name.trim(), email: newCustomer.email, phone: newCustomer.phone, address: (newCustomer as any).address, type: newCustomer.type, creditLimit: newCustomer.creditLimit || '0', currency: newCustomer.currency, isActive: true, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() } as any;
    setCustomers(prev => [optimistic, ...prev]);
    try {
      const created = await customerService.createCustomer({ ...newCustomer, name: optimistic.name, customerNumber: optimistic.customerNumber });
      setCustomers(prev => prev.map(c => c.id === optimistic.id ? ({ ...optimistic, ...created }) : c));
      push({ type: 'success', title: 'Customer Created', message: created.name });
  setCreateOpen(false); setNewCustomer({ customerNumber: '', name: '', type: CTEnum.INDIVIDUAL, creditLimit: '0', currency: Currency.USD });
      fetchCustomers();
    } catch (err: any) {
      setCustomers(prev => prev.filter(c => c.id !== optimistic.id));
      setCreateError(err?.message || 'Create failed');
    } finally { setCreateSubmitting(false); }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault(); if (!selectedCustomer || !editDraft) return; if (!editDraft.name?.trim()) { setEditError('Name required'); return; }
    setEditSubmitting(true); setEditError(null);
    const original = selectedCustomer;
    const optimistic = { ...selectedCustomer, ...editDraft, name: editDraft.name.trim(), updatedAt: new Date().toISOString() } as EnrichedCustomer;
    setCustomers(prev => prev.map(c => c.id === original.id ? optimistic : c));
    setSelectedCustomer(optimistic);
    try {
      const updated = await customerService.updateCustomer(original.id, { name: optimistic.name, email: optimistic.email, phone: (optimistic as any).phone, address: optimistic.address, type: optimistic.type, creditLimit: optimistic.creditLimit, currency: optimistic.currency });
      setCustomers(prev => prev.map(c => c.id === original.id ? ({ ...optimistic, ...updated }) : c));
      setSelectedCustomer(prev => prev && prev.id === original.id ? ({ ...optimistic, ...updated }) : prev);
      push({ type: 'success', title: 'Customer Updated', message: updated.name });
      setEditOpen(false);
    } catch (err: any) {
      setCustomers(prev => prev.map(c => c.id === original.id ? original : c));
      setSelectedCustomer(original);
      setEditError(err?.message || 'Update failed');
    } finally { setEditSubmitting(false); }
  };

  const handleDelete = async (c: EnrichedCustomer) => {
    const ok = await confirm(); if (!ok) return;
    setDeleteSubmitting(c.id);
    const prev = customers;
    setCustomers(list => list.filter(x => x.id !== c.id));
    if (selectedCustomer?.id === c.id) setSelectedCustomer(null);
    try {
      await customerService.deleteCustomer(c.id);
      push({ type: 'success', message: 'Customer deleted' });
      fetchCustomers();
    } catch (err: any) {
      setCustomers(prev);
      push({ type: 'error', title: 'Delete Failed', message: err?.message || 'Unable to delete customer' });
    } finally { setDeleteSubmitting(null); }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Customer Management</h1>
          <p className="text-white/70">Manage your customer relationships and accounts</p>
        </div>
        <div className="flex space-x-2">
          <PermissionGuard anyOf={['customers:create']} fallback={null}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={startCreate}>
              <Plus className="w-4 h-4 mr-2" /> Add Customer
            </Button>
          </PermissionGuard>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            Import CSV
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-white/70 text-sm">Total Customers</p>
                <p className="text-white text-xl">{total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Placeholder KPI until backend supplies segmentation */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-white/70 text-sm">Active (est.)</p>
                <p className="text-white text-xl">{Math.max(total - 0, 0)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-8 h-8 text-purple-400" />
              <div>
                <p className="text-white/70 text-sm">Loaded Page</p>
                <p className="text-white text-xl">{page}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-8 h-8 text-orange-400" />
              <div>
                <p className="text-white/70 text-sm">A/R (placeholder)</p>
                <p className="text-white text-xl">—</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                  <Input
                    placeholder="Search customers..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <div className="flex space-x-2">
                  <select value={statusFilter} onChange={e=>{ setStatusFilter(e.target.value); setPage(1); fetchCustomers({ page:1 }); }} className="bg-white/10 border-white/20 text-white text-xs rounded px-2 py-2">
                    <option value="all">All Status</option>
                    <option value="ACTIVE">Active</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                  <select value={typeFilter} onChange={e=> { setTypeFilter(e.target.value as any); setPage(1); fetchCustomers({ page:1 }); }} className="bg-white/10 border-white/20 text-white text-xs rounded px-2 py-2">
                    <option value="all">All Types</option>
                    <option value="INDIVIDUAL">Individual</option>
                    <option value="COMPANY">Company</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Customer Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Customer List</CardTitle>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="p-4 mb-4 bg-red-500/10 border border-red-500/20 rounded text-red-300 text-sm">
                  {error} <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={() => fetchCustomers()}>Retry</Button>
                </div>
              )}
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Customer</TableHead>
                    <TableHead className="text-white/70">Contact</TableHead>
                    <TableHead className="text-white/70">Total Spent</TableHead>
                    <TableHead className="text-white/70">Orders</TableHead>
                    <TableHead className="text-white/70">A/R Balance</TableHead>
                    <TableHead className="text-white/70">Status</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={7} className="py-10 text-center text-white/60">
                        <Loader2 className="w-5 h-5 mr-2 inline animate-spin" /> Loading customers...
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredCustomers.length === 0 && !error && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={7} className="py-10 text-center text-white/60">
                        No customers found
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredCustomers.map((customer) => (
                    <TableRow 
                      key={customer.id} 
                      className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedCustomer?.id === customer.id ? 'bg-white/10' : ''}`}
                      onClick={() => setSelectedCustomer(customer)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src="" />
                            <AvatarFallback className="bg-white/20 text-white text-xs">
                              {getInitials(customer.name || customer.email || 'C')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white text-sm">{customer.name || customer.email}</p>
                            <p className="text-white/70 text-xs">Last order: {customer.lastOrder || '—'}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Mail className="w-3 h-3 text-white/50" />
                            <span className="text-white/70 text-xs">{customer.email}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Phone className="w-3 h-3 text-white/50" />
                            <span className="text-white/70 text-xs">{(customer as any).phone || '—'}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-white">${(customer.totalSpent ?? 0).toLocaleString()}</TableCell>
                      <TableCell className="text-white/70">{customer.orders ?? 0}</TableCell>
                      <TableCell className={(customer.arBalance ?? 0) > 0 ? "text-yellow-400" : "text-green-400"}>
                        ${(customer.arBalance ?? 0).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor((customer as any).status || (customer as any).tagStatus || 'active')}>
                          {(customer as any).status || (customer as any).tagStatus || 'active'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <PermissionGuard anyOf={['customers:update']} fallback={null}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); startEdit(customer); }}>
                              <Edit className="w-4 h-4" />
                            </Button>
                          </PermissionGuard>
                          <PermissionGuard anyOf={['customers:delete']} fallback={null}>
                            <Button disabled={deleteSubmitting===customer.id} size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); handleDelete(customer); }}>
                              {deleteSubmitting===customer.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                            </Button>
                          </PermissionGuard>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {/* Pagination Controls */}
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
                    onClick={() => { const newPage = page - 1; setPage(newPage); fetchCustomers({ page: newPage }); }}
                  >Prev</Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page >= Math.ceil(total / size) || loading}
                    className="border-white/30 text-white/70 hover:text-white"
                    onClick={() => { const newPage = page + 1; setPage(newPage); fetchCustomers({ page: newPage }); }}
                  >Next</Button>
                  <select
                    value={size}
                    onChange={(e) => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); fetchCustomers({ page: 1, size: newSize }); }}
                    className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none"
                  >
                    {[10,25,50].map(s => <option key={s} value={s}>{s}/page</option>)}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Customer Detail */}
        <div className="space-y-4">
          {selectedCustomer ? (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Customer Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src="" />
                      <AvatarFallback className="bg-white/20 text-white">
                        {getInitials(selectedCustomer.name || selectedCustomer.email || 'C')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="text-white">{selectedCustomer.name || selectedCustomer.email}</h3>
                      <Badge className={getStatusColor((selectedCustomer as any).status || (selectedCustomer as any).tagStatus || 'active')}>
                        {(selectedCustomer as any).status || (selectedCustomer as any).tagStatus || 'active'}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Mail className="w-4 h-4 text-white/50" />
                      <span className="text-white/70 text-sm">{selectedCustomer.email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Phone className="w-4 h-4 text-white/50" />
                      <span className="text-white/70 text-sm">{(selectedCustomer as any).phone || '—'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Account Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <DollarSign className="w-6 h-6 text-green-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Total Spent</p>
                      <p className="text-white">${(selectedCustomer.totalSpent ?? 0).toLocaleString()}</p>
                    </div>
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <ShoppingCart className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Total Orders</p>
                      <p className="text-white">{selectedCustomer.orders ?? 0}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-white/70 text-sm">Balance</span>
                      <span className="text-sm font-medium flex items-center gap-2">
                        {balanceLoadingId === selectedCustomer.id && <Loader2 className="w-3 h-3 animate-spin text-white/50" />}
                        {selectedCustomer.balance !== undefined ? (
                          <span className={Number(selectedCustomer.balance) > 0 ? 'text-yellow-400' : 'text-green-400'}>
                            ${Number(selectedCustomer.balance).toLocaleString()}
                          </span>
                        ) : (
                          <span className="text-white/40">—</span>
                        )}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-white/70 text-sm">Credit Limit</span>
                      <span className="text-white text-sm">${Number(selectedCustomer.creditLimit || 0).toLocaleString()} {selectedCustomer.currency}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-white/70 text-sm">Type</span>
                      <Badge className="bg-white/10 border-white/20 text-white text-xs">{selectedCustomer.type}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-white/70 text-sm">Status</span>
                      <Badge className={getStatusColor((selectedCustomer as any).status || 'active')}>
                        {(selectedCustomer as any).status || 'active'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Last Order</span>
                      <span className="text-white/70 text-sm">{selectedCustomer.lastOrder || '—'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Avg Order Value</span>
                      <span className="text-white text-sm">
                        {selectedCustomer.totalSpent && selectedCustomer.orders
                          ? `$${Math.round((selectedCustomer.totalSpent)/(selectedCustomer.orders || 1)).toLocaleString()}`
                          : '—'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                    <Plus className="w-4 h-4 mr-2" />
                    New Sale
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    <Mail className="w-4 h-4 mr-2" />
                    Send Email
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    View History
                  </Button>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-8 text-center">
                <Users className="w-12 h-12 text-white/50 mx-auto mb-4" />
                <p className="text-white/70">Select a customer to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      {createOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-md">
            <form onSubmit={handleCreate}>
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-white font-medium text-sm">Create Customer</h2>
                <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setCreateOpen(false)}>×</Button>
              </div>
              <div className="p-4 space-y-4">
                {createError && <div className="text-xs text-red-400">{createError}</div>}
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Name *</label>
                  <Input value={newCustomer.name} onChange={e=> setNewCustomer(c=> ({ ...c, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Customer name" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Email</label>
                    <Input value={newCustomer.email||''} onChange={e=> setNewCustomer(c=> ({ ...c, email: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Email" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Phone</label>
                    <Input value={(newCustomer as any).phone||''} onChange={e=> setNewCustomer(c=> ({ ...c, phone: e.target.value } as any))} className="bg-white/10 border-white/20 text-white" placeholder="Phone" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Type</label>
                    <select value={newCustomer.type} onChange={e=> setNewCustomer(c=> ({ ...c, type: e.target.value as CustomerType }))} className="bg-white/10 border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                      <option value="INDIVIDUAL">Individual</option>
                      <option value="COMPANY">Company</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Credit Limit</label>
                    <Input value={newCustomer.creditLimit} onChange={e=> setNewCustomer(c=> ({ ...c, creditLimit: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="0" />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Address</label>
                  <Input value={(newCustomer as any).address||''} onChange={e=> setNewCustomer(c=> ({ ...c, address: e.target.value } as any))} className="bg-white/10 border-white/20 text-white" placeholder="Address" />
                </div>
              </div>
              <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setCreateOpen(false)} disabled={createSubmitting}>Cancel</Button>
                <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={createSubmitting}>{createSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editOpen && selectedCustomer && editDraft && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-md">
            <form onSubmit={handleEdit}>
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-white font-medium text-sm">Edit Customer</h2>
                <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setEditOpen(false)}>×</Button>
              </div>
              <div className="p-4 space-y-4">
                {editError && <div className="text-xs text-red-400">{editError}</div>}
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Name *</label>
                  <Input value={editDraft.name||''} onChange={e=> setEditDraft(d=> ({ ...d!, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Email</label>
                    <Input value={editDraft.email||''} onChange={e=> setEditDraft(d=> ({ ...d!, email: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Phone</label>
                    <Input value={(editDraft as any).phone||''} onChange={e=> setEditDraft(d=> ({ ...d!, phone: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Type</label>
                    <select value={editDraft.type} onChange={e=> setEditDraft(d=> ({ ...d!, type: e.target.value as CustomerType }))} className="bg-white/10 border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                      <option value="INDIVIDUAL">Individual</option>
                      <option value="COMPANY">Company</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-white/70">Credit Limit</label>
                    <Input value={editDraft.creditLimit as any || ''} onChange={e=> setEditDraft(d=> ({ ...d!, creditLimit: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Address</label>
                  <Input value={editDraft.address||''} onChange={e=> setEditDraft(d=> ({ ...d!, address: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                </div>
              </div>
              <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setEditOpen(false)} disabled={editSubmitting}>Cancel</Button>
                <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={editSubmitting}>{editSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDialog}
    </div>
  );
}