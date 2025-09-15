import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useUpdateInventoryStockSettings } from '../hooks/useInventoryQueries';
import { useToast } from '../context/ToastContext';
import { Require } from './Require';

interface UpdateStockSettingsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  product: any | null;
}

export const UpdateStockSettingsModal: React.FC<UpdateStockSettingsModalProps> = ({ open, onOpenChange, product }) => {
  const updateMutation = useUpdateInventoryStockSettings();
  const { push } = useToast();
  const [minStock, setMinStock] = useState<string>('');
  const [maxStock, setMaxStock] = useState<string>('');
  const [reorderPoint, setReorderPoint] = useState<string>('');

  useEffect(() => {
    if (product) {
      setMinStock((product.min_stock ?? product.minStock ?? '').toString());
      setMaxStock((product.max_stock ?? product.maxStock ?? '').toString());
      setReorderPoint((product.reorder_point ?? product.reorderPoint ?? '').toString());
    } else {
      setMinStock(''); setMaxStock(''); setReorderPoint('');
    }
  }, [product]);

  const disabled = updateMutation.isPending;
  const productId = product?.product_id || product?.id;

  const submit = async () => {
    if (!productId) return;
    const min = minStock !== '' ? parseInt(minStock, 10) : undefined;
    const max = maxStock !== '' ? parseInt(maxStock, 10) : undefined;
    const reorder = reorderPoint !== '' ? parseInt(reorderPoint, 10) : undefined;
    if (min !== undefined && max !== undefined && max < min) {
      push({ type: 'warning', title: 'Validation', message: 'Max stock cannot be less than Min stock.' });
      return;
    }
    try {
      await updateMutation.mutateAsync({ productId, minStock: min, maxStock: max, reorderPoint: reorder });
      onOpenChange(false);
    } catch (e) { /* toast handled */ }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!updateMutation.isPending) onOpenChange(o); }}>
      <DialogContent className="bg-slate-900 border border-white/20 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white text-lg">Stock Settings</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div>
            <p className="text-sm text-white/60">Product</p>
            <p className="text-sm text-white font-medium">{product?.name || '—'}</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-xs uppercase text-white/50">Min</label>
              <Input type="number" value={minStock} onChange={e => setMinStock(e.target.value)} className="bg-white/10 border-white/20 text-white" />
            </div>
            <div>
              <label className="text-xs uppercase text-white/50">Max</label>
              <Input type="number" value={maxStock} onChange={e => setMaxStock(e.target.value)} className="bg-white/10 border-white/20 text-white" />
            </div>
            <div>
              <label className="text-xs uppercase text-white/50">Reorder</label>
              <Input type="number" value={reorderPoint} onChange={e => setReorderPoint(e.target.value)} className="bg-white/10 border-white/20 text-white" />
            </div>
          </div>
        </div>
        <DialogFooter className="flex justify-end space-x-2 pt-2">
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10" disabled={disabled} onClick={() => onOpenChange(false)}>Cancel</Button>
          <Require anyOf={['products:update']}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={disabled} onClick={submit}>
              {updateMutation.isPending ? 'Saving...' : 'Save'}
            </Button>
          </Require>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
