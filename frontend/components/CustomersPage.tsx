import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Plus, Search, Users, DollarSign, ShoppingCart, Calendar, Eye, Edit, Mail, Phone, Loader2, Trash2, AlertTriangle } from 'lucide-react';
import { customerService } from '../services/customers';
import { mapError } from '../lib/errorMap';
import { SkeletonTable } from './SkeletonTable';
import { queryKeys } from '../lib/queryKeys';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useUrlQuerySync } from '../hooks/useUrlQuerySync';
import type { Customer, CreateCustomerRequest, CustomerType, CustomerStatus } from '../types';
import { Currency, CustomerType as CTEnum } from '../types';
import { useAuth } from '../context/AuthContext';
import { Require } from './Require';
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
  const debouncedSearch = useDebouncedValue(searchTerm, 300);
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState<'all' | CustomerType>('all');
  const [selectedCustomer, setSelectedCustomer] = useState<EnrichedCustomer | null>(null);
  const [customers, setCustomers] = useState<EnrichedCustomer[]>([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  // Mutation derived UI states (removed explicit useState setters)
  const [deleteSubmitting, setDeleteSubmitting] = useState<number | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const [newCustomer, setNewCustomer] = useState<CreateCustomerRequest>({ customerNumber: '', name: '', type: CTEnum.INDIVIDUAL, creditLimit: '0', currency: Currency.USD });
  const [editDraft, setEditDraft] = useState<Partial<Customer> | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [balanceLoadingId, setBalanceLoadingId] = useState<number | null>(null);
  const balanceLoadedRef = React.useRef<Set<number>>(new Set());

  const debouncedFetchRef = React.useRef<number | null>(null);

  const queryClient = useQueryClient();
  const customersQueryKey = queryKeys.customers({ page, size, search: debouncedSearch, type: typeFilter, status: statusFilter });
  const { isLoading: loading } = useQuery({
    queryKey: customersQueryKey,
    enabled: hasPermission('customers:view'),
    placeholderData: (prev) => prev,
    queryFn: async () => {
      setError(null);
      const resp = await customerService.getCustomers({
        page,
        size,
  q: debouncedSearch || undefined,
        type: typeFilter === 'all' ? undefined : typeFilter,
        status: statusFilter === 'all' ? undefined : statusFilter.toUpperCase() as CustomerStatus
      });
      setCustomers(resp.items as EnrichedCustomer[]);
      setTotal(resp.pagination.total);
      return resp;
    }
  });

  // React to debounced search / filter changes
  useEffect(() => { setPage(1); queryClient.invalidateQueries({ queryKey: ['customers'] }); }, [debouncedSearch, typeFilter, statusFilter, queryClient]);

  useUrlQuerySync({
    state: { page, size, search: debouncedSearch },
    keys: ['page','size','search'],
    encode: (k, v) => {
      if (v == null || v === '' || (k === 'page' && v === 1) || (k === 'size' && v === 10)) return undefined;
      return String(v);
    },
    replace: true,
  });

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

  const createCustomerMutation = useMutation({
    mutationFn: async (payload: CreateCustomerRequest & { tempId: number }) => {
      const { tempId, ...rest } = payload as any;
      return customerService.createCustomer(rest);
    },
    onMutate: async (vars: any) => {
      setCreateError(null);
      if (!vars.name?.trim()) {
        setCreateError('Name required');
        throw new Error('Validation');
      }
      const optimistic: EnrichedCustomer = {
        id: vars.tempId,
        customerNumber: vars.customerNumber,
        name: vars.name.trim(),
        email: vars.email,
        phone: vars.phone,
        address: (vars as any).address,
        type: vars.type,
        creditLimit: vars.creditLimit || '0',
        currency: vars.currency,
        isActive: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      } as any;
      setCustomers(prev => [optimistic, ...prev]);
      return { tempId: vars.tempId };
    },
    onError: (err, _vars, ctx) => {
      setCustomers(prev => prev.filter(c => c.id !== ctx?.tempId));
      const mapped = mapError(err);
      setCreateError(mapped.uiMessage);
      push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Create Failed', message: mapped.uiMessage });
    },
    onSuccess: (created: any, _vars, ctx) => {
      setCustomers(prev => prev.map(c => c.id === ctx?.tempId ? ({ ...c, ...created, id: created.id }) : c));
      push({ type: 'success', title: 'Customer Created', message: created.name });
      setCreateOpen(false);
      setNewCustomer({ customerNumber: '', name: '', type: CTEnum.INDIVIDUAL, creditLimit: '0', currency: Currency.USD });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    }
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    const tempId = Date.now() * -1;
    createCustomerMutation.mutate({ ...newCustomer, name: newCustomer.name.trim(), customerNumber: newCustomer.customerNumber || `CUST-${Date.now()}`, tempId });
  };

  const updateCustomerMutation = useMutation({
    mutationFn: async (vars: { id: number; data: Partial<Customer> }) => customerService.updateCustomer(vars.id, vars.data as any),
    onMutate: (vars) => {
      setEditError(null);
      const original = customers.find(c => c.id === vars.id);
      if (!original) return { original: null };
      const optimistic = { ...original, ...vars.data, name: (vars.data.name || original.name).trim(), updatedAt: new Date().toISOString() } as EnrichedCustomer;
      setCustomers(prev => prev.map(c => c.id === vars.id ? optimistic : c));
      if (selectedCustomer?.id === vars.id) setSelectedCustomer(optimistic);
      return { original };
    },
    onError: (err, vars, ctx) => {
      if (ctx?.original) {
        setCustomers(prev => prev.map(c => c.id === ctx.original!.id ? ctx.original! : c));
        if (selectedCustomer?.id === ctx.original!.id) setSelectedCustomer(ctx.original as any);
      }
      const mapped = mapError(err);
      setEditError(mapped.uiMessage);
      push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Update Failed', message: mapped.uiMessage });
    },
    onSuccess: (updated: any) => {
      setCustomers(prev => prev.map(c => c.id === updated.id ? ({ ...c, ...updated }) : c));
      if (selectedCustomer?.id === updated.id) setSelectedCustomer(prev => prev ? ({ ...prev, ...updated }) : prev);
      push({ type: 'success', title: 'Customer Updated', message: updated.name });
      setEditOpen(false);
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    }
  });

  const handleEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomer || !editDraft) return;
    if (!editDraft.name?.trim()) { setEditError('Name required'); return; }
    updateCustomerMutation.mutate({ id: selectedCustomer.id, data: { ...editDraft, name: editDraft.name.trim() } });
  };

  const deleteCustomerMutation = useMutation({
    mutationFn: async (id: number) => customerService.deleteCustomer(id),
    onMutate: async (id) => {
      setDeleteSubmitting(id);
      const prev = customers;
      setCustomers(list => list.filter(c => c.id !== id));
      if (selectedCustomer?.id === id) setSelectedCustomer(null);
      return { prev };
    },
    onError: (err, id, ctx) => {
      setCustomers(ctx?.prev || []);
      const mapped = mapError(err);
      push({ type: mapped.severity === 'error' ? 'error' : 'warning', title: 'Delete Failed', message: mapped.uiMessage });
    },
    onSuccess: () => {
      push({ type: 'success', message: 'Customer deleted' });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
    onSettled: () => setDeleteSubmitting(null)
  });

  const handleDelete = async (c: EnrichedCustomer) => {
    const ok = await confirm(); if (!ok) return;
    deleteCustomerMutation.mutate(c.id);
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
          <Require anyOf={['customers:create']}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={startCreate}>
              <Plus className="w-4 h-4 mr-2" /> Add Customer
            </Button>
          </Require>
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
                  <select value={statusFilter} onChange={e=>{ setStatusFilter(e.target.value); setPage(1); }} className="bg-white/10 border-white/20 text-white text-xs rounded px-2 py-2">
                    <option value="all">All Status</option>
                    <option value="ACTIVE">Active</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                  <select value={typeFilter} onChange={e=> { setTypeFilter(e.target.value as any); setPage(1); }} className="bg-white/10 border-white/20 text-white text-xs rounded px-2 py-2">
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
                  {error} <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={() => queryClient.invalidateQueries({ queryKey: ['customers'] })}>Retry</Button>
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
                    <TableRow><TableCell colSpan={7} className="p-0"><SkeletonTable columns={7} rows={6} /></TableCell></TableRow>
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
                          <Require anyOf={['customers:update']}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); startEdit(customer); }}>
                              <Edit className="w-4 h-4" />
                            </Button>
                          </Require>
                          <Require anyOf={['customers:delete']}>
                            <Button disabled={deleteSubmitting===customer.id} size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); handleDelete(customer); }}>
                              {deleteSubmitting===customer.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                            </Button>
                          </Require>
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
                    onClick={() => { const newPage = page - 1; setPage(newPage); }}
                  >Prev</Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page >= Math.ceil(total / size) || loading}
                    className="border-white/30 text-white/70 hover:text-white"
                    onClick={() => { const newPage = page + 1; setPage(newPage); }}
                  >Next</Button>
                  <select
                    value={size}
                    onChange={(e) => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); }}
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
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setCreateOpen(false)} disabled={createCustomerMutation.isPending}>Cancel</Button>
                <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={createCustomerMutation.isPending}>{createCustomerMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}</Button>
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
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setEditOpen(false)} disabled={updateCustomerMutation.isPending}>Cancel</Button>
                <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={updateCustomerMutation.isPending}>{updateCustomerMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDialog}
    </div>
  );
}