import React, { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from './ui/pagination';
import { Plus, Search, Building2, Users, MapPin, Phone, Eye, Edit, Trash2, Loader2, AlertTriangle } from 'lucide-react';
import type { Branch, CreateBranchRequest } from '../types';
import { branchesService } from '../services/branches';
import { useToast } from '../context/ToastContext';
import { useConfirm } from './ConfirmDialog';

interface BranchPerformance { sales: string; revenue: string; topProducts?: Array<{ name: string; totalSold: number }>; }

export function BranchesPage() {
  const { push } = useToast();
  const { confirm, dialog: confirmDialog } = useConfirm();

  // Data state
  const [branches, setBranches] = useState<Branch[]>([]);
  const [selected, setSelected] = useState<Branch | null>(null);
  const [performance, setPerformance] = useState<BranchPerformance | null>(null);
  const [perfLoading, setPerfLoading] = useState(false);

  // UI / control state
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [deleteSubmitting, setDeleteSubmitting] = useState<number | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const [newBranch, setNewBranch] = useState<CreateBranchRequest>({ name: '' });
  const [editDraft, setEditDraft] = useState<Partial<Branch> | null>(null);

  const totalPages = Math.max(1, Math.ceil(total / size));

  const fetchBranches = useCallback(async (override?: { page?: number; size?: number; term?: string }) => {
    setLoading(true); setError(null);
    try {
      const resp = await branchesService.getBranches({
        page: override?.page ?? page,
        size: override?.size ?? size,
        q: (override?.term ?? search) || undefined
      });
      setBranches(resp.items as Branch[]);
      setTotal(resp.pagination.total);
      if (!selected && resp.items.length) setSelected(resp.items[0] as Branch);
    } catch (e: any) {
      setError(e?.message || 'Failed to load branches');
    } finally {
      setLoading(false);
    }
  }, [page, size, search, selected]);

  // Debounced search
  useEffect(() => { const t = setTimeout(() => { setPage(1); fetchBranches({ page:1 }); }, 350); return () => clearTimeout(t); }, [search, fetchBranches]);
  useEffect(() => { fetchBranches(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load performance when selected changes
  useEffect(() => {
    if (!selected) { setPerformance(null); return; }
    let active = true;
    (async () => {
      setPerfLoading(true);
      try {
        const perf = await branchesService.getBranchPerformance(selected.id).catch(()=>null);
        if (active) setPerformance(perf as any);
      } finally { if (active) setPerfLoading(false); }
    })();
    return () => { active = false; };
  }, [selected]);

  const startCreate = () => { setNewBranch({ name: '' }); setCreateError(null); setShowCreate(true); };
  const startEdit = (b: Branch) => { setSelected(b); setEditDraft({ name: b.name, address: b.address, phone: b.phone, email: b.email, isActive: b.isActive, status: b.status }); setEditError(null); setShowEdit(true); };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBranch.name.trim()) { setCreateError('Name is required'); return; }
    setCreateSubmitting(true); setCreateError(null);
    const optimistic: Branch = { id: Date.now()*-1, name: newBranch.name.trim(), address: newBranch.address, phone: newBranch.phone, email: newBranch.email, isActive: true, status: 'ACTIVE', createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() } as Branch;
    setBranches(prev => [optimistic, ...prev]);
    try {
      const created = await branchesService.createBranch({ name: optimistic.name, address: optimistic.address, phone: optimistic.phone, email: optimistic.email } as CreateBranchRequest);
      setBranches(prev => prev.map(b => b.id === optimistic.id ? ({ ...optimistic, ...created }) : b));
      setSelected(s => s && s.id === optimistic.id ? ({ ...optimistic, ...created }) : s);
      push({ type: 'success', title: 'Branch Created', message: created.name });
      setShowCreate(false); setNewBranch({ name: '' });
      fetchBranches();
    } catch (err: any) {
      setBranches(prev => prev.filter(b => b.id !== optimistic.id));
      setCreateError(err?.message || 'Failed to create branch');
    } finally { setCreateSubmitting(false); }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault(); if (!selected || !editDraft) return;
    if (!editDraft.name?.trim()) { setEditError('Name is required'); return; }
    setEditSubmitting(true); setEditError(null);
    const original = selected;
    const optimistic = { ...selected, ...editDraft, name: editDraft.name.trim(), updatedAt: new Date().toISOString() } as Branch;
    setBranches(prev => prev.map(b => b.id === original.id ? optimistic : b));
    setSelected(optimistic);
    try {
      const updated = await branchesService.updateBranch(original.id, { name: optimistic.name, address: optimistic.address, phone: optimistic.phone, email: optimistic.email, isActive: optimistic.isActive, status: optimistic.status });
      setBranches(prev => prev.map(b => b.id === original.id ? ({ ...optimistic, ...updated }) : b));
      setSelected(prev => prev && prev.id === original.id ? ({ ...optimistic, ...updated }) : prev);
      push({ type: 'success', title: 'Branch Updated', message: updated.name });
      setShowEdit(false);
    } catch (err: any) {
      setBranches(prev => prev.map(b => b.id === original.id ? original : b));
      setSelected(original); setEditError(err?.message || 'Update failed');
    } finally { setEditSubmitting(false); }
  };

  const handleDelete = async (b: Branch) => {
    const ok = await confirm(); if (!ok) return;
    setDeleteSubmitting(b.id);
    const prev = branches;
    setBranches(list => list.filter(x => x.id !== b.id));
    if (selected?.id === b.id) setSelected(null);
    try {
      await branchesService.deleteBranch(b.id);
      push({ type: 'success', message: 'Branch deleted' });
      fetchBranches();
    } catch (err: any) {
      push({ type: 'error', title: 'Delete Failed', message: err?.message || 'Could not delete branch' });
      setBranches(prev);
    } finally { setDeleteSubmitting(null); }
  };

  const getStatusBadge = (b: Branch) => {
    const active = b.status === 'ACTIVE' && b.isActive !== false;
    return active ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const visible = branches; // server filtered

  return (
    <>
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Branch Management</h1>
          <p className="text-white/70">Manage your business locations and operations</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={startCreate}>
            <Plus className="w-4 h-4 mr-2" /> Add Branch
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input placeholder="Search branches..." value={search} onChange={e=>setSearch(e.target.value)} className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Branches</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Name</TableHead>
                    <TableHead className="text-white/70">Address</TableHead>
                    <TableHead className="text-white/70">Phone</TableHead>
                    <TableHead className="text-white/70">Status</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-10 text-center text-white/60"><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Loading branches...</TableCell>
                    </TableRow>
                  )}
                  {!loading && error && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-6">
                        <div className="flex items-center justify-center gap-2 text-red-300 text-sm"><AlertTriangle className="w-4 h-4" /> {error}</div>
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && !error && visible.length === 0 && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-10 text-center text-white/50 text-sm">No branches found</TableCell>
                    </TableRow>
                  )}
                  {!loading && !error && visible.map(b => (
                    <TableRow key={b.id} className={`border-white/10 cursor-pointer hover:bg-white/5 ${selected?.id === b.id ? 'bg-white/10' : ''}`} onClick={()=>setSelected(b)}>
                      <TableCell className="text-white">
                        <div className="space-y-0.5">
                          <p>{b.name}</p>
                          {b.email && <p className="text-xs text-white/50">{b.email}</p>}
                        </div>
                      </TableCell>
                      <TableCell className="text-white/70 text-sm max-w-[200px] truncate">{b.address || '-'}</TableCell>
                      <TableCell className="text-white/70 text-sm">{b.phone || '-'}</TableCell>
                      <TableCell>
                        <Badge className={getStatusBadge(b)}>{(b.status || (b.isActive?'ACTIVE':'INACTIVE'))}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={e=>{e.stopPropagation(); setSelected(b);}}><Eye className="w-4 h-4" /></Button>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={e=>{e.stopPropagation(); startEdit(b);}}><Edit className="w-4 h-4" /></Button>
                          <Button disabled={deleteSubmitting===b.id} size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={e=>{e.stopPropagation(); handleDelete(b);}}>{deleteSubmitting===b.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}</Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-4 flex items-center justify-between text-xs text-white/60">
                <div>{total} total • Page {page}/{totalPages}</div>
                <Pagination>
                  <PaginationContent>
                    <PaginationItem>
                      <PaginationPrevious onClick={()=> setPage(p => Math.max(1, p-1))} className={page===1? 'pointer-events-none opacity-40' : ''} />
                    </PaginationItem>
                    {Array.from({ length: totalPages }).slice(0,5).map((_,i) => {
                      const p = i+1; return (
                        <PaginationItem key={p}>
                          <PaginationLink isActive={p===page} onClick={()=> setPage(p)}>{p}</PaginationLink>
                        </PaginationItem>
                      );
                    })}
                    <PaginationItem>
                      <PaginationNext onClick={()=> setPage(p => Math.min(totalPages, p+1))} className={page===totalPages? 'pointer-events-none opacity-40' : ''} />
                    </PaginationItem>
                  </PaginationContent>
                </Pagination>
              </div>
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          {selected && (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader><CardTitle className="text-white">Branch Details</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-white text-lg">{selected.name}</h3>
                    <Badge className={getStatusBadge(selected)}>{selected.status}</Badge>
                  </div>
                  <div className="space-y-3 text-sm">
                    {selected.address && <div className="flex items-start gap-2"><MapPin className="w-4 h-4 text-white/50 mt-0.5" /><span className="text-white/70">{selected.address}</span></div>}
                    {selected.phone && <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-white/50" /><span className="text-white/70">{selected.phone}</span></div>}
                    {selected.email && <div className="flex items-center gap-2"><Users className="w-4 h-4 text-white/50" /><span className="text-white/70">{selected.email}</span></div>}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader><CardTitle className="text-white">Performance</CardTitle></CardHeader>
                <CardContent>
                  {perfLoading && <div className="text-white/60 text-sm flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Loading performance...</div>}
                  {!perfLoading && performance && (
                    <div className="space-y-2 text-sm text-white/70">
                      <div><span className="text-white/60">Sales:</span> {performance.sales}</div>
                      <div><span className="text-white/60">Revenue:</span> {performance.revenue}</div>
                      {performance.topProducts && performance.topProducts.length>0 && (
                        <div>
                          <div className="text-white/60 mb-1">Top Products</div>
                          <ul className="list-disc pl-4 space-y-0.5">
                            {performance.topProducts.slice(0,5).map((tp,i)=>(<li key={i}>{tp.name} – {tp.totalSold}</li>))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  {!perfLoading && !performance && <div className="text-white/50 text-xs">No performance data</div>}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>

    {/* Create Modal */}
    {showCreate && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-md">
          <form onSubmit={handleCreate}>
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-white font-medium text-sm">Create Branch</h2>
              <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setShowCreate(false)}>×</Button>
            </div>
            <div className="p-4 space-y-4">
              {createError && <div className="text-xs text-red-400">{createError}</div>}
              <div className="space-y-1">
                <label className="text-xs text-white/70">Name *</label>
                <Input value={newBranch.name} onChange={e=> setNewBranch(b=> ({ ...b, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Branch name" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-white/70">Address</label>
                <Input value={newBranch.address||''} onChange={e=> setNewBranch(b=> ({ ...b, address: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Address" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Phone</label>
                  <Input value={newBranch.phone||''} onChange={e=> setNewBranch(b=> ({ ...b, phone: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Phone" />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Email</label>
                  <Input value={newBranch.email||''} onChange={e=> setNewBranch(b=> ({ ...b, email: e.target.value }))} className="bg-white/10 border-white/20 text-white" placeholder="Email" />
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
              <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setShowCreate(false)} disabled={createSubmitting}>Cancel</Button>
              <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={createSubmitting}>{createSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}</Button>
            </div>
          </form>
        </div>
      </div>
    )}

    {/* Edit Modal */}
    {showEdit && selected && editDraft && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <div className="bg-zinc-900 border border-white/10 rounded-lg w-full max-w-md">
          <form onSubmit={handleEdit}>
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-white font-medium text-sm">Edit Branch</h2>
              <Button type="button" variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={()=> setShowEdit(false)}>×</Button>
            </div>
            <div className="p-4 space-y-4">
              {editError && <div className="text-xs text-red-400">{editError}</div>}
              <div className="space-y-1">
                <label className="text-xs text-white/70">Name *</label>
                <Input value={editDraft.name||''} onChange={e=> setEditDraft(d=> ({ ...d!, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-white/70">Address</label>
                <Input value={editDraft.address||''} onChange={e=> setEditDraft(d=> ({ ...d!, address: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Phone</label>
                  <Input value={editDraft.phone||''} onChange={e=> setEditDraft(d=> ({ ...d!, phone: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-white/70">Email</label>
                  <Input value={editDraft.email||''} onChange={e=> setEditDraft(d=> ({ ...d!, email: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs text-white/70">Status</label>
                <select value={editDraft.status} onChange={e=> setEditDraft(d=> ({ ...d!, status: e.target.value as any }))} className="bg-white/10 border border-white/20 text-white text-sm rounded px-2 py-2 w-full">
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                </select>
              </div>
            </div>
            <div className="p-4 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20 rounded-b-lg">
              <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={()=> setShowEdit(false)} disabled={editSubmitting}>Cancel</Button>
              <Button type="submit" className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={editSubmitting}>{editSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save'}</Button>
            </div>
          </form>
        </div>
      </div>
    )}

    {confirmDialog}
    </>
  );
}