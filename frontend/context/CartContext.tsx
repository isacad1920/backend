import React, { createContext, useContext, useMemo, useState, useCallback, useEffect } from 'react';
import type { Product } from '../types';

export interface CartItem {
  product: Product;
  quantity: number; // whole units only for now
  discountPercent?: number; // optional % discount (0-100)
  discountFixed?: number; // fixed currency amount per line (applied after percent)
}

interface CartContextValue {
  items: CartItem[];
  addProduct: (product: Product, qty?: number) => void;
  updateQuantity: (productId: number, qty: number) => void;
  removeProduct: (productId: number) => void;
  clear: () => void;
  subtotal: number; // numeric convenience (sum of unitPrice * qty)
  discountTotal: number; // aggregate discount value
  netSubtotal: number; // subtotal - discount
  totalQuantity: number;
  setLineDiscountPercent: (productId: number, percent?: number) => void;
  setLineDiscountFixed: (productId: number, amount?: number) => void;
}

const CartContext = createContext<CartContextValue | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>(() => {
    try {
      const raw = localStorage.getItem('pos.cart.v1');
      if (!raw) return [];
      const parsed = JSON.parse(raw) as CartItem[];
      return Array.isArray(parsed) ? parsed : [];
    } catch { return []; }
  });

  // persist
  useEffect(() => {
    try { localStorage.setItem('pos.cart.v1', JSON.stringify(items)); } catch {/* ignore */}
  }, [items]);

  const addProduct = useCallback((product: Product, qty: number = 1) => {
    setItems(prev => {
      const existing = prev.find(i => i.product.id === product.id);
      if (existing) {
        return prev.map(i => i.product.id === product.id ? { ...i, quantity: i.quantity + qty } : i);
      }
      return [...prev, { product, quantity: qty }];
    });
  }, []);

  const updateQuantity = useCallback((productId: number, qty: number) => {
    setItems(prev => prev.flatMap(i => {
      if (i.product.id !== productId) return [i];
      if (qty <= 0) return []; // remove if zero or negative
      return [{ ...i, quantity: qty }];
    }));
  }, []);

  const setLineDiscountPercent = useCallback((productId: number, percent?: number) => {
    setItems(prev => prev.map(i => i.product.id === productId ? { ...i, discountPercent: percent } : i));
  }, []);

  const setLineDiscountFixed = useCallback((productId: number, amount?: number) => {
    setItems(prev => prev.map(i => i.product.id === productId ? { ...i, discountFixed: amount } : i));
  }, []);

  const removeProduct = useCallback((productId: number) => {
    setItems(prev => prev.filter(i => i.product.id !== productId));
  }, []);

  const clear = useCallback(() => setItems([]), []);

  const subtotal = useMemo(() => {
    return items.reduce((acc, item) => acc + (Number(item.product.sellingPrice || 0) * item.quantity), 0);
  }, [items]);

  const discountTotal = useMemo(() => {
    return items.reduce((acc, item) => {
      const unit = Number(item.product.sellingPrice || 0);
      const lineBase = unit * item.quantity;
      const pct = item.discountPercent ? (lineBase * (item.discountPercent / 100)) : 0;
      const fixed = item.discountFixed ? Math.min(lineBase - pct, item.discountFixed) : 0;
      return acc + pct + fixed;
    }, 0);
  }, [items]);

  const netSubtotal = useMemo(() => Math.max(0, subtotal - discountTotal), [subtotal, discountTotal]);

  const totalQuantity = useMemo(() => items.reduce((acc, i) => acc + i.quantity, 0), [items]);

  const value: CartContextValue = {
    items,
    addProduct,
    updateQuantity,
    removeProduct,
    clear,
    subtotal,
    discountTotal,
    netSubtotal,
    totalQuantity,
    setLineDiscountPercent,
    setLineDiscountFixed,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
