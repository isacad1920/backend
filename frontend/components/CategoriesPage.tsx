import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { 
  Plus, 
  Search, 
  Tag, 
  Package,
  Edit,
  Trash2,
  Eye,
  Loader2,
  AlertTriangle
} from 'lucide-react';
import { categoriesService } from '../services/categories';
import { useToast } from '../context/ToastContext';
import type { Category } from '../types';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from './ui/pagination';
import { useConfirm } from './ConfirmDialog';

interface EnrichedCategory extends Category {
  productCount?: number; // placeholder until backend provides aggregated counts
  totalValue?: number;   // placeholder
  parentId?: number | null; // if backend adds hierarchy later
}

export function CategoriesPage() {
  const { push } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState<EnrichedCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<EnrichedCategory | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [deleteSubmitting, setDeleteSubmitting] = useState<number | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const [newCategory, setNewCategory] = useState<{ name: string; description: string }>({ name: '', description: '' });
  const [editCategory, setEditCategory] = useState<{ name: string; description: string } | null>(null);
  const { confirm, dialog: confirmDialog } = useConfirm();

  const fetchCategories = useCallback(async (override?: { page?: number; size?: number; term?: string }) => {
    setLoading(true); setError(null);
    try {
      const resp = await categoriesService.getCategories({
        page: override?.page ?? page,
        size: override?.size ?? size,
        q: (override?.term ?? searchTerm) || undefined
      });
      // Enrich placeholders
      const enriched = resp.items.map(c => ({ ...c, productCount: (c as any).productCount, totalValue: (c as any).totalValue }));
      setCategories(enriched as EnrichedCategory[]);
      setTotal(resp.pagination.total);
      if (!selectedCategory && enriched.length) setSelectedCategory(enriched[0] as EnrichedCategory);
    } catch (e: any) {
      setError(e?.message || 'Failed to load categories');
    } finally {
      setLoading(false);
    }
  }, [page, size, searchTerm, selectedCategory]);

  useEffect(() => { fetchCategories(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const handle = setTimeout(() => { setPage(1); fetchCategories({ page:1 }); }, 300);
    return () => clearTimeout(handle);
  }, [searchTerm, fetchCategories]);

  const filteredCategories = categories; // server side

  const getParentName = (parentId: number | null | undefined) => 'Root Category'; // placeholder until hierarchy backend
  const getChildCategories = (parentId: number) => categories.filter(cat => cat.parentId === parentId);

  const startEdit = (cat: EnrichedCategory) => {
    setEditCategory({ name: cat.name, description: cat.description || '' });
    setEditError(null);
    setShowEdit(true);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategory.name.trim()) { setCreateError('Name is required'); return; }
    setCreateSubmitting(true); setCreateError(null);
    const optimistic: EnrichedCategory = { id: Date.now() * -1, name: newCategory.name.trim(), description: newCategory.description.trim(), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), productCount: 0, totalValue: 0 } as any;
    setCategories(prev => [optimistic, ...prev]);
    try {
      const created = await categoriesService.createCategory({ name: optimistic.name, description: optimistic.description || undefined });
      setCategories(prev => prev.map(c => c.id === optimistic.id ? ({ ...optimistic, ...created }) : c));
      setSelectedCategory(c => c && c.id === optimistic.id ? ({ ...optimistic, ...created }) : c);
      push({ type: 'success', title: 'Category Created', message: created.name });
      setShowCreate(false);
      setNewCategory({ name: '', description: '' });
      fetchCategories();
    } catch (err: any) {
      setCategories(prev => prev.filter(c => c.id !== optimistic.id));
      setCreateError(err?.message || 'Failed to create category');
    } finally {
      setCreateSubmitting(false);
    }
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategory || !editCategory) return;
    if (!editCategory.name.trim()) { setEditError('Name is required'); return; }
    setEditSubmitting(true); setEditError(null);
    const original = selectedCategory;
    const optimistic = { ...selectedCategory, name: editCategory.name.trim(), description: editCategory.description.trim() } as EnrichedCategory;
    setCategories(prev => prev.map(c => c.id === optimistic.id ? optimistic : c));
    setSelectedCategory(optimistic);
    try {
      const updated = await categoriesService.updateCategory(original.id, { name: optimistic.name, description: optimistic.description || undefined });
      setCategories(prev => prev.map(c => c.id === original.id ? ({ ...optimistic, ...updated }) : c));
      setSelectedCategory(prev => prev && prev.id === original.id ? ({ ...optimistic, ...updated }) : prev);
      push({ type: 'success', title: 'Category Updated', message: updated.name });
      setShowEdit(false);
    } catch (err: any) {
      setEditError(err?.message || 'Update failed');
      setCategories(prev => prev.map(c => c.id === original.id ? original : c));
      setSelectedCategory(original);
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleDelete = async (cat: EnrichedCategory) => {
    const ok = await confirm();
    if (!ok) return;
    setDeleteSubmitting(cat.id);
    const prev = categories;
    setCategories(list => list.filter(c => c.id !== cat.id));
    if (selectedCategory?.id === cat.id) setSelectedCategory(null);
    try {
      await categoriesService.deleteCategory(cat.id);
      push({ type: 'success', message: 'Category deleted' });
      fetchCategories();
    } catch (err: any) {
      push({ type: 'error', title: 'Delete Failed', message: err?.message || 'Could not delete category' });
      setCategories(prev);
    } finally {
      setDeleteSubmitting(null);
    }
  };

  return (
    <>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Category Management</h1>
          <p className="text-white/70">Organize your products into categories</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Category
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input
                  placeholder="Search categories..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
            </CardContent>
          </Card>

          {/* Category Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Category</TableHead>
                    <TableHead className="text-white/70">Parent</TableHead>
                    <TableHead className="text-white/70">Products</TableHead>
                    <TableHead className="text-white/70">Total Value</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-10 text-center text-white/60"><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Loading categories...</TableCell>
                    </TableRow>
                  )}
                  {!loading && error && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-6">
                        <div className="flex items-center justify-center gap-2 text-red-300 text-sm"><AlertTriangle className="w-4 h-4" /> {error}</div>
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && !error && filteredCategories.length === 0 && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={5} className="py-10 text-center text-white/60">No categories found</TableCell>
                    </TableRow>
                  )}
                  {!loading && !error && filteredCategories.map((category) => (
                    <TableRow 
                      key={category.id} 
                      className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedCategory?.id === category.id ? 'bg-white/10' : ''}`}
                      onClick={() => setSelectedCategory(category)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Tag className="w-4 h-4 text-blue-400" />
                          <div>
                            <p className="text-white">{category.name}</p>
                            <p className="text-white/70 text-sm">{category.description}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-white/70">{getParentName(category.parentId)}</TableCell>
                      <TableCell className="text-white">{category.productCount}</TableCell>
                      <TableCell className="text-white">${(category.totalValue ?? 0).toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => startEdit(category)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" disabled={deleteSubmitting === category.id} className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => handleDelete(category)}>
                            {deleteSubmitting === category.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
          {/* Pagination Controls */}
          <div className="flex items-center justify-between py-2">
            <div className="text-xs text-white/60">Page {page} of {Math.max(1, Math.ceil(total / size))} • {total} total</div>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    onClick={(e) => { e.preventDefault(); if (page > 1) { setPage(p => p - 1); fetchCategories({ page: page - 1 }); } }}
                    className={page === 1 ? 'pointer-events-none opacity-40' : ''}
                  />
                </PaginationItem>
                {[...Array(Math.min(5, Math.max(1, Math.ceil(total / size))))].map((_, idx) => {
                  const totalPages = Math.max(1, Math.ceil(total / size));
                  let start = Math.max(1, Math.min(page - 2, totalPages - 4));
                  const pageNumber = start + idx;
                  if (pageNumber > totalPages) return null;
                  return (
                    <PaginationItem key={pageNumber}>
                      <PaginationLink
                        href="#"
                        isActive={pageNumber === page}
                        onClick={(e) => { e.preventDefault(); setPage(pageNumber); fetchCategories({ page: pageNumber }); }}
                      >{pageNumber}</PaginationLink>
                    </PaginationItem>
                  );
                })}
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    onClick={(e) => { e.preventDefault(); const totalPages = Math.max(1, Math.ceil(total / size)); if (page < totalPages) { setPage(p => p + 1); fetchCategories({ page: page + 1 }); } }}
                    className={page >= Math.max(1, Math.ceil(total / size)) ? 'pointer-events-none opacity-40' : ''}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
            <div className="flex items-center gap-2 text-xs text-white/60">
              <span>Rows:</span>
              {[10,25,50].map(s => (
                <button
                  key={s}
                  onClick={() => { setSize(s); setPage(1); fetchCategories({ page:1, size:s }); }}
                  className={`px-2 py-1 rounded border text-white/70 hover:text-white hover:bg-white/10 ${size===s ? 'bg-white/20 border-white/40' : 'border-white/20'}`}
                >{s}</button>
              ))}
            </div>
          </div>
        </div>

        {/* Category Details */}
        <div className="space-y-4">
          {selectedCategory && (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Category Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Tag className="w-6 h-6 text-blue-400" />
                    <div>
                      <h3 className="text-white">{selectedCategory.name}</h3>
                      <p className="text-white/70 text-sm">{selectedCategory.description}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Parent Category</span>
                      <span className="text-white text-sm">{getParentName(selectedCategory.parentId)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Product Count</span>
                      <span className="text-white text-sm">{selectedCategory.productCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Total Value</span>
                      <span className="text-white text-sm">${(selectedCategory.totalValue ?? 0).toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Package className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Products</p>
                      <p className="text-white text-lg">{selectedCategory.productCount}</p>
                    </div>
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Tag className="w-6 h-6 text-green-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Subcategories</p>
                      <p className="text-white text-lg">{getChildCategories(selectedCategory.id).length}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {getChildCategories(selectedCategory.id).length > 0 && (
                <Card className="bg-white/10 backdrop-blur-md border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Subcategories</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {getChildCategories(selectedCategory.id).map((child) => (
                        <div key={child.id} className="flex items-center justify-between p-2 bg-white/5 rounded">
                          <div className="flex items-center space-x-2">
                            <Tag className="w-3 h-3 text-blue-400" />
                            <span className="text-white text-sm">{child.name}</span>
                          </div>
                          <span className="text-white/70 text-xs">{child.productCount} items</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Subcategory
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    <Package className="w-4 h-4 mr-2" />
                    View Products
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10" onClick={() => startEdit(selectedCategory)}>
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Category
                  </Button>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  {showCreate && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div className="w-full max-w-md bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
          <form onSubmit={handleCreate} className="flex flex-col max-h-[80vh]">
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
              <h2 className="text-white text-lg font-medium">Add Category</h2>
              <button type="button" onClick={() => setShowCreate(false)} className="text-white/60 hover:text-white">✕</button>
            </div>
            <div className="px-5 py-4 space-y-4 overflow-y-auto">
              {createError && <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-sm p-2 rounded flex items-start"><AlertTriangle className="w-4 h-4 mr-2 mt-0.5" /> {createError}</div>}
              <div>
                <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Name<span className="text-red-400">*</span></label>
                <Input value={newCategory.name} onChange={e => setNewCategory(c => ({ ...c, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Description</label>
                <Input value={newCategory.description} onChange={e => setNewCategory(c => ({ ...c, description: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
            </div>
            <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
              <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button type="submit" disabled={createSubmitting} className="bg-white/20 hover:bg-white/30 text-white border border-white/30 disabled:opacity-50">
                {createSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Create
              </Button>
            </div>
          </form>
        </div>
      </div>
    )}
  {showEdit && editCategory && selectedCategory && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div className="w-full max-w-md bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
          <form onSubmit={handleEdit} className="flex flex-col max-h-[80vh]">
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
              <h2 className="text-white text-lg font-medium">Edit Category</h2>
              <button type="button" onClick={() => setShowEdit(false)} className="text-white/60 hover:text-white">✕</button>
            </div>
            <div className="px-5 py-4 space-y-4 overflow-y-auto">
              {editError && <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-sm p-2 rounded flex items-start"><AlertTriangle className="w-4 h-4 mr-2 mt-0.5" /> {editError}</div>}
              <div>
                <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Name<span className="text-red-400">*</span></label>
                <Input value={editCategory!.name} onChange={e => setEditCategory(c => c && ({ ...c, name: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Description</label>
                <Input value={editCategory!.description} onChange={e => setEditCategory(c => c && ({ ...c, description: e.target.value }))} className="bg-white/10 border-white/20 text-white" />
              </div>
            </div>
            <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
              <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={() => setShowEdit(false)}>Cancel</Button>
              <Button type="submit" disabled={editSubmitting} className="bg-white/20 hover:bg-white/30 text-white border border-white/30 disabled:opacity-50">
                {editSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Save
              </Button>
            </div>
          </form>
        </div>
      </div>
    )}
    {confirmDialog}
    </>
  );
}