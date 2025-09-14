import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { ShoppingCart, Plus, Minus, Trash2, CreditCard, DollarSign, Search, Package, Receipt, User, Loader2, RefreshCw, Percent, X, Wallet } from 'lucide-react';
import { productService } from '../services/products';
import type { Product } from '../types';
import { useCart } from '../context/CartContext';
import { customerService } from '../services/customers';
import type { Customer, Currency, PaymentMethod } from '../types';
import { salesService } from '../services/sales';
import { useAuth } from '../context/AuthContext';

const categories = ['All']; // dynamic categories can be introduced later

export function POSPage() {
  const { items: cart, addProduct, updateQuantity, removeProduct, clear, subtotal, discountTotal, netSubtotal, setLineDiscountPercent, setLineDiscountFixed } = useCart();
  const { user } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [customerName, setCustomerName] = useState<string>('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [customerResults, setCustomerResults] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const customerDebounceRef = React.useRef<number | null>(null);
  // Customer live search
  const searchCustomers = useCallback(async (term: string) => {
    if (!term.trim()) { setCustomerResults([]); return; }
    try {
      const resp = await customerService.getCustomers({ page: 1, size: 5, q: term });
      setCustomerResults(resp.items as Customer[]);
    } catch {/* swallow */}
  }, []);

  useEffect(() => {
    if (customerDebounceRef.current) window.clearTimeout(customerDebounceRef.current);
    customerDebounceRef.current = window.setTimeout(() => { searchCustomers(customerSearch); }, 300);
    return () => { if (customerDebounceRef.current) window.clearTimeout(customerDebounceRef.current); };
  }, [customerSearch, searchCustomers]);

  interface PendingPayment { method: 'cash' | 'card' | 'credit'; amount: number; id: string; }
  const [payments, setPayments] = useState<PendingPayment[]>([]);
  const addPayment = (method: PendingPayment['method'], amount: number) => {
    if (amount <= 0) return;
    setPayments(prev => [...prev, { method, amount, id: Math.random().toString(36).slice(2) }]);
  };
  const removePayment = (id: string) => setPayments(prev => prev.filter(p => p.id !== id));
  const paymentTotal = payments.reduce((a, p) => a + p.amount, 0);
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'card'>('cash');
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(24);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debouncedRef = React.useRef<number | null>(null);

  const fetchProducts = useCallback(async (override?: { page?: number; size?: number; term?: string }) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await productService.getProducts({
        page: override?.page ?? page,
        size: override?.size ?? size,
        q: (override?.term ?? searchTerm) || undefined,
      });
      setProducts(resp.items as Product[]);
      setTotal(resp.pagination.total);
    } catch (e: any) {
      setError(e?.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  }, [page, size, searchTerm]);

  useEffect(() => { fetchProducts(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (debouncedRef.current) window.clearTimeout(debouncedRef.current);
    debouncedRef.current = window.setTimeout(() => {
      setPage(1);
      fetchProducts({ page: 1 });
    }, 300);
    return () => { if (debouncedRef.current) window.clearTimeout(debouncedRef.current); };
  }, [searchTerm, fetchProducts]);

  const filteredProducts = products.filter(p => {
    const matchesCategory = selectedCategory === 'All'; // future: p.category?.name === selectedCategory
    return matchesCategory;
  });

  const tax = netSubtotal * 0.08;
  const totalDue = netSubtotal + tax;

  const processPayment = async () => {
    if (cart.length === 0) {
      toast.error('Cart is empty');
      return;
    }
    if (Math.abs(paymentTotal - totalDue) > 0.01) {
      toast.error('Payment total does not match amount due');
      return;
    }
    // Basic credit validation: prevent credit method if no customer selected
    if (payments.some(p => p.method === 'credit') && !selectedCustomer) {
      toast.error('Credit payment requires a selected customer');
      return;
    }
    // Prepare sale payload for backend
    try {
      const salePayload = {
        branchId: user?.branchId || 1, // assumption; adjust when branch selector exists
        customerId: selectedCustomer?.id,
        userId: user?.id || 0,
        items: cart.map(ci => ({
          productId: ci.product.id,
          quantity: ci.quantity,
          unitPrice: String(ci.product.sellingPrice || '0'),
          discount: ci.discountPercent || ci.discountFixed ? String(
            // convert combined discount value for this line to an approximate per-line amount
            (() => {
              const unit = Number(ci.product.sellingPrice || 0);
              const lineBase = unit * ci.quantity;
              const pct = ci.discountPercent ? (lineBase * (ci.discountPercent / 100)) : 0;
              const fixed = ci.discountFixed ? Math.min(lineBase - pct, ci.discountFixed) : 0;
              return pct + fixed;
            })()
          ) : '0'
        })),
        payments: payments.map(p => ({
          accountId: 1, // placeholder; real UI will choose account
          amount: String(p.amount.toFixed(2)),
          method: p.method === 'credit' ? 'CREDIT' : (p.method === 'cash' ? 'CASH' : 'CARD') as PaymentMethod,
          currency: 'USD' as Currency,
        })),
        notes: selectedCustomer ? `POS sale for ${selectedCustomer.name}` : 'Walk-in POS sale'
      };
      await salesService.createSale(salePayload as any);
      toast.success(`Sale recorded: $${totalDue.toFixed(2)}`);
      clear();
      setSelectedCustomer(null);
      setPayments([]);
    } catch (e: any) {
      toast.error(e?.message || 'Failed to record sale');
    }
  };

  return (
    <div className="h-screen flex bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Products Section */}
      <div className="flex-1 p-6 overflow-hidden">
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-white text-2xl mb-2">Point of Sale</h1>
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input
                  placeholder="Search products or SKU..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                disabled={loading}
                onClick={() => fetchProducts()}
                className="border-white/30 text-white hover:bg-white/10"
              >
                <RefreshCw className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
                Reload
              </Button>
              
              {/* Category Filter */}
              <div className="flex space-x-2">
                {categories.map(category => (
                  <Button
                    key={category}
                    variant={selectedCategory === category ? "default" : "outline"}
                    className={selectedCategory === category 
                      ? "bg-white/20 text-white border-white/30" 
                      : "border-white/30 text-white hover:bg-white/10"
                    }
                    onClick={() => setSelectedCategory(category)}
                  >
                    {category}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1 overflow-y-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {loading && (
                <div className="col-span-full text-center text-white/60 py-10">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading products...
                </div>
              )}
              {!loading && error && (
                <div className="col-span-full text-center text-red-300 text-sm py-4">
                  {error} <Button size="sm" variant="ghost" className="ml-2 text-red-200 hover:text-white" onClick={() => fetchProducts()}>Retry</Button>
                </div>
              )}
              {!loading && !error && filteredProducts.length === 0 && (
                <div className="col-span-full text-center text-white/60 py-10">No products found</div>
              )}
              {!loading && !error && filteredProducts.map(product => (
                <Card
                  key={product.id}
                  className="bg-white/10 backdrop-blur-md border-white/20 cursor-pointer hover:bg-white/15 transition-colors"
                  onClick={() => addProduct(product)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-center w-12 h-12 bg-white/20 rounded-lg mb-3 mx-auto">
                      <Package className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-white text-sm font-medium text-center mb-1">{product.name}</h3>
                    <p className="text-white/70 text-xs text-center mb-2">{product.sku}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-white font-medium">${Number(product.sellingPrice || 0).toLocaleString()}</span>
                      <Badge variant="secondary" className="bg-white/20 text-white text-xs">
                        {(product as any).stock?.quantity ?? '—'}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="flex items-center justify-between mt-4 text-white/60 text-xs">
              <div>Page {page} of {Math.max(1, Math.ceil(total / size))}</div>
              <div className="flex space-x-2">
                <Button size="sm" variant="outline" disabled={page <= 1 || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => { const newPage = page - 1; setPage(newPage); fetchProducts({ page: newPage }); }}>Prev</Button>
                <Button size="sm" variant="outline" disabled={page >= Math.ceil(total / size) || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => { const newPage = page + 1; setPage(newPage); fetchProducts({ page: newPage }); }}>Next</Button>
                <select value={size} onChange={(e) => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); fetchProducts({ page: 1, size: newSize }); }} className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none">
                  {[12,24,48].map(s => <option key={s} value={s}>{s}/page</option>)}
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cart Section */}
      <div className="w-96 bg-white/10 backdrop-blur-md border-l border-white/20 flex flex-col">
        {/* Cart Header */}
        <div className="p-6 border-b border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-xl flex items-center">
              <ShoppingCart className="w-5 h-5 mr-2" />
              Cart ({cart.length})
            </h2>
            {cart.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clear}
                className="text-white/70 hover:text-white hover:bg-white/10"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Customer Picker */}
          <div className="space-y-2 relative">
            <label className="text-white/70 text-sm">Customer (Optional)</label>
            {selectedCustomer ? (
              <div className="flex items-center justify-between bg-white/10 border border-white/20 rounded px-3 py-2 text-white text-sm">
                <span>{selectedCustomer.name}</span>
                <Button size="sm" variant="ghost" className="text-white/60 hover:text-white" onClick={() => setSelectedCustomer(null)}><X className="w-4 h-4" /></Button>
              </div>
            ) : (
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input
                  placeholder="Search customer..."
                  value={customerSearch}
                  onChange={(e) => setCustomerSearch(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
                {customerResults.length > 0 && (
                  <div className="absolute z-20 mt-1 w-full bg-slate-900/95 backdrop-blur border border-white/20 rounded shadow-lg max-h-52 overflow-auto">
                    {customerResults.map(c => (
                      <button
                        key={c.id}
                        className="w-full text-left px-3 py-2 text-xs text-white/80 hover:bg-white/10"
                        onClick={() => { setSelectedCustomer(c); setCustomerResults([]); setCustomerSearch(''); }}
                      >{c.name}</button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-6">
          {cart.length === 0 ? (
            <div className="text-center text-white/70 mt-8">
              <ShoppingCart className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Cart is empty</p>
              <p className="text-sm">Add products to start a sale</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cart.map(item => (
                <div key={item.product.id} className="bg-white/5 rounded-lg p-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="text-white text-sm">{item.product.name}</h4>
                      <p className="text-white/70 text-xs">${Number(item.product.sellingPrice || 0)} each</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeProduct(item.product.id)}
                      className="text-white/50 hover:text-white hover:bg-white/10 h-6 w-6 p-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                        className="h-7 w-7 p-0 border-white/30 text-white hover:bg-white/10"
                      >
                        <Minus className="w-3 h-3" />
                      </Button>
                      <span className="text-white w-8 text-center">{item.quantity}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                        className="h-7 w-7 p-0 border-white/30 text-white hover:bg-white/10"
                      >
                        <Plus className="w-3 h-3" />
                      </Button>
                    </div>
                    <div className="text-right space-y-1 w-28">
                      <div className="text-white font-medium text-xs">${(Number(item.product.sellingPrice || 0) * item.quantity).toFixed(2)}</div>
                      <div className="flex items-center space-x-1">
                        <Percent className="w-3 h-3 text-white/40" />
                        <input
                          type="number"
                          min={0}
                          max={100}
                          value={item.discountPercent ?? ''}
                          onChange={(e) => {
                            const v = e.target.value === '' ? undefined : Math.min(100, Math.max(0, Number(e.target.value)));
                            setLineDiscountPercent(item.product.id, v);
                          }}
                          className="w-12 bg-white/10 border border-white/20 rounded px-1 py-0.5 text-white text-xs focus:outline-none"
                          placeholder="%"
                        />
                        <input
                          type="number"
                          min={0}
                          value={item.discountFixed ?? ''}
                          onChange={(e) => {
                            const v = e.target.value === '' ? undefined : Math.max(0, Number(e.target.value));
                            setLineDiscountFixed(item.product.id, v);
                          }}
                          className="w-14 bg-white/10 border border-white/20 rounded px-1 py-0.5 text-white text-xs focus:outline-none"
                          placeholder="$"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cart Footer */}
        {cart.length > 0 && (
          <div className="border-t border-white/20 p-6">
            {/* Totals */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-white/70">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              {discountTotal > 0 && (
                <div className="flex justify-between text-green-300 text-xs">
                  <span>Discounts</span>
                  <span>- ${discountTotal.toFixed(2)}</span>
                </div>
              )}
              {discountTotal > 0 && (
                <div className="flex justify-between text-white/70">
                  <span>Net Subtotal</span>
                  <span>${netSubtotal.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-white/70">
                <span>Tax (8%)</span>
                <span>${tax.toFixed(2)}</span>
              </div>
              <div className="h-px bg-white/20" />
              <div className="flex justify-between text-white text-lg font-medium">
                <span>Total</span>
                <span>${totalDue.toFixed(2)}</span>
              </div>
            </div>

            {/* Multi-Payment Builder */}
            <div className="mb-4 space-y-2">
              <div className="flex items-center justify-between text-white/70 text-xs">
                <span className="flex items-center"><Wallet className="w-4 h-4 mr-1" /> Payments</span>
                <span>${paymentTotal.toFixed(2)} / ${totalDue.toFixed(2)}</span>
              </div>
              <div className="flex space-x-2">
                {(['cash','card','credit'] as const).map(m => (
                  <Button key={m} size="sm" variant="outline" className="border-white/30 text-white/80 hover:text-white" onClick={() => addPayment(m, Number((totalDue - paymentTotal).toFixed(2)))} disabled={paymentTotal >= totalDue}>
                    {m}
                  </Button>
                ))}
              </div>
              <div className="space-y-1 max-h-24 overflow-auto pr-1">
                {payments.map(p => (
                  <div key={p.id} className="flex items-center justify-between bg-white/5 rounded px-2 py-1 text-xs text-white/70">
                    <span>{p.method}</span>
                    <div className="flex items-center space-x-2">
                      <span>${p.amount.toFixed(2)}</span>
                      <button onClick={() => removePayment(p.id)} className="text-white/40 hover:text-white"><X className="w-3 h-3" /></button>
                    </div>
                  </div>
                ))}
                {payments.length === 0 && <div className="text-white/40 text-xs">No payments yet</div>}
              </div>
            </div>

            {/* (Legacy single payment method section removed in favor of multi-payment builder) */}

            {/* Process Payment Button */}
            <Button onClick={processPayment} className="w-full bg-green-600 hover:bg-green-700 text-white">
              <Receipt className="w-4 h-4 mr-2" /> Process Payment ${totalDue.toFixed(2)}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}