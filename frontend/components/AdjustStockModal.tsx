import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { useAdjustInventoryStock } from '../hooks/useInventoryQueries';
import { useToast } from '../context/ToastContext';
import { Require } from './Require';

interface AdjustStockModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  product: any | null;
}

export const AdjustStockModal: React.FC<AdjustStockModalProps> = ({ open, onOpenChange, product }) => {
  const { push } = useToast();
  const adjustMutation = useAdjustInventoryStock();
  const [delta, setDelta] = useState<string>('');
  const [reason, setReason] = useState('');

  const disabled = adjustMutation.isPending;
  const productId = product?.product_id || product?.id;

  const submit = async () => {
    if (!productId) return;
    const adj = parseInt(delta, 10);
    if (isNaN(adj) || adj === 0) {
      push({ type: 'warning', title: 'Invalid Quantity', message: 'Enter a non-zero number.' });
      return;
    }
    try {
      await adjustMutation.mutateAsync({ productId, adjustment: adj, reason: reason || 'Manual adjustment' });
      onOpenChange(false);
      setDelta('');
      setReason('');
    } catch (e) {
      // toast handled in mutation onError
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!adjustMutation.isPending) onOpenChange(o); }}>
      <DialogContent className="bg-slate-900 border border-white/20 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white text-lg">Adjust Stock</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div>
            <p className="text-sm text-white/60">Product</p>
            <p className="text-sm text-white font-medium">{product?.name || '—'}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs uppercase text-white/50">Current Qty</label>
              <div className="mt-1 text-white/80 text-sm">{product?.quantity ?? '—'}</div>
            </div>
            <div>
              <label className="text-xs uppercase text-white/50">Delta (+/-)</label>
              <Input type="number" value={delta} onChange={e => setDelta(e.target.value)} className="bg-white/10 border-white/20 text-white" placeholder="e.g. 5 or -2" />
            </div>
          </div>
          <div>
            <label className="text-xs uppercase text-white/50">Reason</label>
            <Textarea value={reason} onChange={e => setReason(e.target.value)} className="bg-white/10 border-white/20 text-white resize-none" rows={3} placeholder="e.g. Damaged items written off" />
          </div>
        </div>
        <DialogFooter className="flex justify-end space-x-2 pt-2">
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10" disabled={disabled} onClick={() => onOpenChange(false)}>Cancel</Button>
          <Require anyOf={['inventory:adjust','products:update']}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" disabled={disabled} onClick={submit}>
              {adjustMutation.isPending ? 'Saving...' : 'Apply'}
            </Button>
          </Require>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
