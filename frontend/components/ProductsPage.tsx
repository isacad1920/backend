import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productService } from '../services/products';
import { categoriesService } from '../services/categories';
import type { Product, Category, CreateProductRequest } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from './ui/pagination';
import { useToast } from '../context/ToastContext';
import { useConfirm } from './ConfirmDialog';
import { useOptimisticList } from '../hooks/useOptimisticList';
import { 
  Plus, Search, Tag, Package, Edit, Trash2, Loader2, Layers3, ArchiveRestore, ArrowUpCircle, ArrowDownCircle, DollarSign
} from 'lucide-react';
import { Require } from './Require';
import { SkeletonTable } from './SkeletonTable';
import { queryKeys } from '../lib/queryKeys';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useUrlQuerySync } from '../hooks/useUrlQuerySync';

interface ProductDraft {
  name: string;
  sku?: string;
  description?: string;
  categoryId?: number;
  costPrice?: string; // keep as string to align with backend decimal strings
  sellingPrice?: string;
  barcode?: string;
}

export const ProductsPage: React.FC = () => {
  const { push } = useToast();
  const { confirm, dialog: confirmDialog } = useConfirm();

  // Data state
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 350);
  const [categoryFilter, setCategoryFilter] = useState<number | 'all'>('all');
  const [categories, setCategories] = useState<Category[]>([]);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState<Product | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [createDraft, setCreateDraft] = useState<ProductDraft>({ name: '' });
  const [editDraft, setEditDraft] = useState<ProductDraft>({ name: '' });
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [adjustSubmitting, setAdjustSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const [adjustQty, setAdjustQty] = useState<number>(0);
  const [adjustReason, setAdjustReason] = useState('');
  const [showAdjust, setShowAdjust] = useState(false);

  const { items: products, setItems: setProducts, addOptimistic, replaceId, updateOptimistic, removeOptimistic, rollback } = useOptimisticList<Product>([], { findId: p => (p as any).id });

  const totalPages = Math.max(1, Math.ceil(total / size));

  const queryClient = useQueryClient();
  const productsQueryKey = queryKeys.products({ page, size, search: debouncedSearch, category: categoryFilter });
  const { data: productPage, isLoading: loading } = useQuery({
    queryKey: productsQueryKey,
    placeholderData: (prev) => prev,
    queryFn: async () => {
      setError(null);
      const resp = await productService.getProducts({
        page,
        size,
        q: debouncedSearch || undefined,
        category: categoryFilter === 'all' ? undefined : categoryFilter as number
      });
      setProducts(resp.items as Product[]);
      setTotal(resp.pagination.total);
      if (!selected && resp.items.length) setSelected(resp.items[0]);
      return resp;
    },
  });

  const fetchCategories = useCallback(async () => {
    try {
      const resp = await categoriesService.getCategories({ page:1, size:100 });
      setCategories(resp.items as Category[]);
    } catch (e) { /* silent */ }
  }, []);

  // products automatically loaded by react-query
  useEffect(() => { fetchCategories(); }, [fetchCategories]);
  useEffect(() => { setPage(1); queryClient.invalidateQueries({ queryKey: ['products'] }); }, [debouncedSearch, categoryFilter, queryClient]);

  // Sync key pagination & search params to URL
  useUrlQuerySync({
    state: { page, size, search: debouncedSearch },
    keys: ['page','size','search'],
    encode: (k, v) => {
      if (v == null || v === '' || (k === 'page' && v === 1) || (k === 'size' && v === 25)) return undefined; // omit defaults
      return String(v);
    },
    replace: true,
  });

  const startCreate = () => { setCreateDraft({ name: '', categoryId: typeof categoryFilter === 'number' ? categoryFilter : undefined }); setCreateError(null); setShowCreate(true); };
  const startEdit = (p: Product) => { setSelected(p); setEditDraft({ name: p.name, sku: (p as any).sku, description: (p as any).description, categoryId: (p as any).categoryId, costPrice: (p as any).costPrice, sellingPrice: (p as any).sellingPrice, barcode: (p as any).barcode }); setEditError(null); setShowEdit(true); };
  const startAdjust = (p: Product) => { setSelected(p); setAdjustQty(0); setAdjustReason(''); setShowAdjust(true); };

  const createMutation = useMutation({
    mutationFn: (payload: CreateProductRequest) => productService.createProduct(payload),
    onSuccess: (created) => {
      replaceId(tempIdRef.current!, created);
      push({ type: 'success', title: 'Product Created', message: created.name });
      setShowCreate(false);
      setCreateDraft({ name: '' });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (err: any) => {
      rollback();
      setCreateError(err?.message || 'Failed to create product');
    },
    onSettled: () => setCreateSubmitting(false)
  });
  const tempIdRef = React.useRef<number | null>(null);
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createDraft.name.trim()) { setCreateError('Name is required'); return; }
    setCreateSubmitting(true); setCreateError(null);
    const optimistic: Product = { id: Date.now() * -1, name: createDraft.name.trim(), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() } as any; addOptimistic(optimistic); tempIdRef.current = optimistic.id as any;
    try {
      const createPayload: CreateProductRequest = {
        sku: createDraft.sku || `SKU-${Date.now()}`,
        name: createDraft.name.trim(),
        barcode: createDraft.barcode || undefined,
        description: createDraft.description || undefined,
        costPrice: createDraft.costPrice || '0',
        sellingPrice: createDraft.sellingPrice || createDraft.costPrice || '0',
        categoryId: createDraft.categoryId || undefined
      };
      createMutation.mutate(createPayload);
    } catch (err: any) {
      rollback();
      setCreateError(err?.message || 'Failed to create product');
    }
  };

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<Product> }) => productService.updateProduct(id, payload as any),
    onSuccess: (updated) => {
      updateOptimistic((updated as any).id, updated as any);
      setSelected(updated);
      push({ type: 'success', title: 'Product Updated', message: (updated as any).name });
      setShowEdit(false);
    },
    onError: (err: any, _vars, ctx: any) => {
      rollback();
      setEditError(err?.message || 'Update failed');
      if (ctx?.original) setSelected(ctx.original);
    },
    onSettled: () => setEditSubmitting(false)
  });
  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return; if (!editDraft.name.trim()) { setEditError('Name required'); return; }
    setEditSubmitting(true); setEditError(null);
    const original = selected;
    updateOptimistic(original.id, { name: editDraft.name.trim(), updatedAt: new Date().toISOString() } as any);
    try {
      const updatePayload = { ...editDraft } as any; // backend accepts partial Product fields
  updateMutation.mutate({ id: (original as any).id, payload: updatePayload });
    } catch (err: any) {
      rollback();
      setEditError(err?.message || 'Update failed');
      setSelected(original);
    }
  };

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productService.deleteProduct(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['products'] }); },
  });
  const handleDelete = async (p: Product) => {
    const ok = await confirm(); if (!ok) return;
    const backup = [...products];
    removeOptimistic((p as any).id);
    try {
      await deleteMutation.mutateAsync((p as any).id);
      push({ type: 'success', message: 'Product deleted' });
      if (selected?.id === (p as any).id) setSelected(null);
    } catch (err: any) {
      setProducts(backup);
      push({ type: 'error', title: 'Delete failed', message: err?.message || 'Unable to delete' });
    }
  };

  const handleAdjust = async (e: React.FormEvent) => {
    e.preventDefault(); if (!selected) return; if (!adjustQty) return;
    setAdjustSubmitting(true);
    try {
      const result = await productService.adjustProductStock((selected as any).id, { productId: (selected as any).id, adjustment: adjustQty, reason: adjustReason || 'Manual adjustment' } as any);
      push({ type: 'success', title: 'Stock Adjusted', message: result.message || 'Adjustment applied' });
      setShowAdjust(false);
    } catch (err: any) {
      push({ type: 'error', title: 'Adjustment Failed', message: err?.message || 'Could not adjust stock' });
    } finally { setAdjustSubmitting(false); }
  };

  const categoryOptions = useMemo(() => [{ id: 'all', name: 'All Categories' }, ...categories.map(c => ({ id: c.id, name: c.name }))], [categories]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Products</h1>
          <p className="text-white/70">Manage product catalog and stock</p>
        </div>
        <div className="flex items-center gap-2">
          <Require anyOf={['products:write']}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={startCreate}>
              <Plus className="w-4 h-4 mr-2"/>Add Product
            </Button>
          </Require>
        </div>
      </div>

      <Card className="bg-white/10 backdrop-blur-md border-white/20">
        <CardContent className="p-4 flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
          <div className="flex items-center gap-2 w-full md:w-1/2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-white/50" />
              <Input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search products..." className="pl-9 bg-white/10 border-white/20 text-white placeholder:text-white/50" />
            </div>
            <select value={categoryFilter} onChange={e=>setCategoryFilter(e.target.value==='all'?'all':Number(e.target.value))} className="bg-white/10 border border-white/20 text-white text-sm rounded px-2 py-2">
              {categoryOptions.map(opt => <option key={opt.id} value={opt.id}>{opt.name}</option>)}
            </select>
          </div>
          <div className="text-xs text-white/60">{total} total • Page {page}/{totalPages}</div>
        </CardContent>
      </Card>

      <Card className="bg-white/10 backdrop-blur-md border-white/20">
        <CardHeader>
          <CardTitle className="text-white">Catalog</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-white/20">
                  <TableHead className="text-white/70">Name</TableHead>
                  <TableHead className="text-white/70">SKU</TableHead>
                  <TableHead className="text-white/70">Category</TableHead>
                  <TableHead className="text-white/70">Cost</TableHead>
                  <TableHead className="text-white/70">Price</TableHead>
                  <TableHead className="text-white/70">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading && (
                  <TableRow><TableCell colSpan={6} className="p-0"><SkeletonTable columns={6} rows={6} /></TableCell></TableRow>
                )}
                {!loading && error && (
                  <TableRow className="border-white/10"><TableCell colSpan={6} className="py-6 text-center text-red-300 text-sm">{error}</TableCell></TableRow>
                )}
                {!loading && !error && products.length === 0 && (
                  <TableRow className="border-white/10"><TableCell colSpan={6} className="py-10 text-center text-white/60">No products found</TableCell></TableRow>
                )}
                {!loading && !error && products.map(p => (
                  <TableRow key={(p as any).id} className={`border-white/20 hover:bg-white/5 cursor-pointer ${selected?.id === (p as any).id ? 'bg-white/10' : ''}`} onClick={()=>setSelected(p)}>
                    <TableCell className="text-white">{p.name}</TableCell>
                    <TableCell className="text-white/60 text-sm">{(p as any).sku || '-'}</TableCell>
                    <TableCell className="text-white/60 text-sm">{categories.find(c => c.id === (p as any).categoryId)?.name || '-'}</TableCell>
                    <TableCell className="text-white/60 text-sm">{(p as any).costPrice ? `$${(p as any).costPrice}` : '-'}</TableCell>
                    <TableCell className="text-white/60 text-sm">{(p as any).sellingPrice ? `$${(p as any).sellingPrice}` : '-'}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Require anyOf={['products:write']}>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); startEdit(p); }}><Edit className="w-4 h-4" /></Button>
                        </Require>
                        <Require anyOf={['products:write']}>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); startAdjust(p); }}><ArchiveRestore className="w-4 h-4" /></Button>
                        </Require>
                        <Require anyOf={['products:delete']}>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e)=>{ e.stopPropagation(); handleDelete(p); }}><Trash2 className="w-4 h-4" /></Button>
                        </Require>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious href="#" onClick={(e)=>{ e.preventDefault(); if (page>1){ setPage(p=>p-1); } }} className={page===1?'pointer-events-none opacity-40':''} />
                </PaginationItem>
                {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                  const start = Math.max(1, Math.min(page - 2, totalPages - 4));
                  const pn = start + idx; if (pn > totalPages) return null;
                  return (
                    <PaginationItem key={pn}>
                      <PaginationLink href="#" isActive={pn===page} onClick={(e)=>{ e.preventDefault(); setPage(pn); }}>{pn}</PaginationLink>
                    </PaginationItem>
                  );
                })}
                <PaginationItem>
                  <PaginationNext href="#" onClick={(e)=>{ e.preventDefault(); if (page<totalPages){ setPage(p=>p+1); } }} className={page===totalPages?'pointer-events-none opacity-40':''} />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
            <div className="flex items-center gap-2 text-xs text-white/60">
              Rows:
              {[10,25,50].map(s => <button key={s} onClick={()=>{ setSize(s); setPage(1); }} className={`px-2 py-1 rounded border ${size===s?'bg-white/20 border-white/40 text-white':'border-white/20 text-white/70 hover:text-white hover:bg-white/10'}`}>{s}</button>)}
            </div>
          </div>
        </CardContent>
      </Card>

      {selected && (
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader><CardTitle className="text-white">Details</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-blue-400" />
              <h3 className="text-white font-medium">{selected.name}</h3>
              {(selected as any).sku && <Badge className="bg-white/20 text-white border-white/30">{(selected as any).sku}</Badge>}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
              <div className="space-y-0.5"><p className="text-white/60">Category</p><p className="text-white">{categories.find(c=>c.id===(selected as any).categoryId)?.name || '-'}</p></div>
              <div className="space-y-0.5"><p className="text-white/60">Cost</p><p className="text-white">{(selected as any).costPrice?`$${(selected as any).costPrice}`:'-'}</p></div>
              <div className="space-y-0.5"><p className="text-white/60">Price</p><p className="text-white">{(selected as any).sellingPrice?`$${(selected as any).sellingPrice}`:'-'}</p></div>
              <div className="space-y-0.5"><p className="text-white/60">Barcode</p><p className="text-white">{(selected as any).barcode || '-'}</p></div>
              <div className="space-y-0.5"><p className="text-white/60">Created</p><p className="text-white text-xs">{new Date(selected.createdAt).toLocaleString()}</p></div>
              <div className="space-y-0.5"><p className="text-white/60">Updated</p><p className="text-white text-xs">{new Date(selected.updatedAt).toLocaleString()}</p></div>
            </div>
            <div className="flex flex-wrap gap-2 pt-2">
              <Require anyOf={['products:write']}>
                <Button size="sm" variant="outline" className="border-white/30 text-white hover:bg-white/10" onClick={()=>startEdit(selected)}><Edit className="w-4 h-4 mr-1" /> Edit</Button>
              </Require>
              <Require anyOf={['products:write']}>
                <Button size="sm" variant="outline" className="border-white/30 text-white hover:bg-white/10" onClick={()=>startAdjust(selected)}><Layers3 className="w-4 h-4 mr-1" /> Adjust Stock</Button>
              </Require>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
            <form onSubmit={handleCreate} className="flex flex-col max-h-[85vh]">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
                <h2 className="text-white text-lg font-medium">Add Product</h2>
                <button type="button" onClick={()=>setShowCreate(false)} className="text-white/60 hover:text-white">✕</button>
              </div>
              <div className="px-5 py-4 space-y-4 overflow-y-auto">
                {createError && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-2 rounded">{createError}</div>}
                <div>
                  <label className="block text-xs text-white/60 mb-1">Name *</label>
                  <Input value={createDraft.name} onChange={e=>setCreateDraft(d=>({...d,name:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-1">SKU</label>
                    <Input value={createDraft.sku||''} onChange={e=>setCreateDraft(d=>({...d,sku:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Barcode</label>
                    <Input value={createDraft.barcode||''} onChange={e=>setCreateDraft(d=>({...d,barcode:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Category</label>
                    <select value={createDraft.categoryId||''} onChange={e=>setCreateDraft(d=>({...d,categoryId:e.target.value?Number(e.target.value):undefined}))} className="w-full bg-white/10 border border-white/20 text-white rounded px-2 py-2 text-sm">
                      <option value="">None</option>
                      {categories.map(c=> <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Cost</label>
                      <Input type="number" value={createDraft.costPrice||''} onChange={e=>setCreateDraft(d=>({...d,costPrice:e.target.value || undefined}))} className="bg-white/10 border-white/20 text-white" />
                    </div>
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Price</label>
                      <Input type="number" value={createDraft.sellingPrice||''} onChange={e=>setCreateDraft(d=>({...d,sellingPrice:e.target.value || undefined}))} className="bg-white/10 border-white/20 text-white" />
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-white/60 mb-1">Description</label>
                  <Input value={createDraft.description||''} onChange={e=>setCreateDraft(d=>({...d,description:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                </div>
              </div>
              <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=>setShowCreate(false)}>Cancel</Button>
                <Button type="submit" disabled={createSubmitting} className="bg-white/20 hover:bg-white/30 text-white border border-white/30">{createSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Create</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEdit && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
            <form onSubmit={handleEdit} className="flex flex-col max-h-[85vh]">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
                <h2 className="text-white text-lg font-medium">Edit Product</h2>
                <button type="button" onClick={()=>setShowEdit(false)} className="text-white/60 hover:text-white">✕</button>
              </div>
              <div className="px-5 py-4 space-y-4 overflow-y-auto">
                {editError && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-2 rounded">{editError}</div>}
                <div>
                  <label className="block text-xs text-white/60 mb-1">Name *</label>
                  <Input value={editDraft.name} onChange={e=>setEditDraft(d=>({...d,name:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-1">SKU</label>
                    <Input value={editDraft.sku||''} onChange={e=>setEditDraft(d=>({...d,sku:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Barcode</label>
                    <Input value={editDraft.barcode||''} onChange={e=>setEditDraft(d=>({...d,barcode:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Category</label>
                    <select value={editDraft.categoryId||''} onChange={e=>setEditDraft(d=>({...d,categoryId:e.target.value?Number(e.target.value):undefined}))} className="w-full bg-white/10 border border-white/20 text-white rounded px-2 py-2 text-sm">
                      <option value="">None</option>
                      {categories.map(c=> <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Cost</label>
                      <Input type="number" value={editDraft.costPrice||''} onChange={e=>setEditDraft(d=>({...d,costPrice:e.target.value || undefined}))} className="bg-white/10 border-white/20 text-white" />
                    </div>
                    <div>
                      <label className="block text-xs text-white/60 mb-1">Price</label>
                      <Input type="number" value={editDraft.sellingPrice||''} onChange={e=>setEditDraft(d=>({...d,sellingPrice:e.target.value || undefined}))} className="bg-white/10 border-white/20 text-white" />
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-white/60 mb-1">Description</label>
                  <Input value={editDraft.description||''} onChange={e=>setEditDraft(d=>({...d,description:e.target.value}))} className="bg-white/10 border-white/20 text-white" />
                </div>
              </div>
              <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=>setShowEdit(false)}>Cancel</Button>
                <Button type="submit" disabled={editSubmitting} className="bg-white/20 hover:bg-white/30 text-white border border-white/30">{editSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Save</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stock Adjustment Modal */}
      {showAdjust && selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
            <form onSubmit={handleAdjust} className="flex flex-col max-h-[80vh]">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
                <h2 className="text-white text-lg font-medium">Adjust Stock</h2>
                <button type="button" onClick={()=>setShowAdjust(false)} className="text-white/60 hover:text-white">✕</button>
              </div>
              <div className="px-5 py-4 space-y-4 overflow-y-auto">
                <p className="text-white/70 text-sm">Enter a positive number to add stock or a negative number to reduce stock.</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Adjustment *</label>
                    <Input type="number" value={adjustQty} onChange={e=>setAdjustQty(Number(e.target.value))} className="bg-white/10 border-white/20 text-white" />
                  </div>
                  <div>
                    <label className="block text-xs text-white/60 mb-1">Reason</label>
                    <Input value={adjustReason} onChange={e=>setAdjustReason(e.target.value)} className="bg-white/10 border-white/20 text-white" />
                  </div>
                </div>
              </div>
              <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
                <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=>setShowAdjust(false)}>Cancel</Button>
                <Button type="submit" disabled={adjustSubmitting || !adjustQty} className="bg-white/20 hover:bg-white/30 text-white border border-white/30 disabled:opacity-50">{adjustSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}Apply</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDialog}
    </div>
  );
};

export default ProductsPage;