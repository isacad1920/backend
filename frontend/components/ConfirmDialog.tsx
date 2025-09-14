import React from 'react';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './ui/alert-dialog';
import { Button } from './ui/button';

export interface ConfirmDialogProps {
  trigger?: React.ReactNode;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  onConfirm: () => Promise<any> | any;
  onOpenChange?: (open: boolean) => void;
  open?: boolean;
  setOpen?: (open: boolean) => void;
  disabled?: boolean;
}

// Controlled + uncontrolled support
export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  trigger,
  title = 'Are you sure?',
  description = 'This action cannot be undone.',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  destructive = true,
  onConfirm,
  onOpenChange,
  open,
  setOpen,
  disabled
}) => {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const effectiveOpen = open !== undefined ? open : internalOpen;
  const changeOpen = (v: boolean) => {
    if (setOpen) setOpen(v); else setInternalOpen(v);
    onOpenChange?.(v);
  };
  const [submitting, setSubmitting] = React.useState(false);
  const handleConfirm = async () => {
    try {
      setSubmitting(true);
      await onConfirm();
      changeOpen(false);
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <AlertDialog open={effectiveOpen} onOpenChange={changeOpen}>
      {trigger && (
        <AlertDialogTrigger asChild>
          <div onClick={() => !disabled && changeOpen(true)}>{trigger}</div>
        </AlertDialogTrigger>
      )}
      <AlertDialogContent className="bg-zinc-900 border border-white/20 text-white">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-white">{title}</AlertDialogTitle>
          {description && <AlertDialogDescription className="text-white/70">{description}</AlertDialogDescription>}
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel className="border-white/30 text-white/80 hover:bg-white/10" onClick={() => changeOpen(false)} disabled={submitting}>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={submitting}
            className={`border border-white/30 ${destructive ? 'bg-red-600 hover:bg-red-500' : 'bg-white/20 hover:bg-white/30'} text-white`}
          >
            {submitting ? 'Working...' : confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export function useConfirm() {
  const [promise, setPromise] = React.useState<{
    resolve: (v: boolean) => void;
  } | null>(null);
  const [open, setOpen] = React.useState(false);
  const confirm = () => new Promise<boolean>(resolve => { setPromise({ resolve }); setOpen(true); });
  const handleConfirm = () => { promise?.resolve(true); setOpen(false); };
  const handleCancel = () => { promise?.resolve(false); setOpen(false); };
  const dialog = (
    <AlertDialog open={open} onOpenChange={(v) => { if (!v) handleCancel(); }}>
      <AlertDialogContent className="bg-zinc-900 border border-white/20 text-white">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-white">Are you sure?</AlertDialogTitle>
          <AlertDialogDescription className="text-white/70">This action cannot be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel className="border-white/30 text-white/80 hover:bg-white/10" onClick={handleCancel}>Cancel</AlertDialogCancel>
          <AlertDialogAction className="border border-white/30 bg-red-600 hover:bg-red-500 text-white" onClick={handleConfirm}>Confirm</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
  return { confirm, dialog };
}
