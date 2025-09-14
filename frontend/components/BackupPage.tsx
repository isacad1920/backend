import React, { useEffect, useState, useCallback } from 'react';
import { backupService, type BackupRecord, type BackupStats, type RestoreResult } from '../services/backups';
import { useToast } from '../context/ToastContext';
import { PermissionGuard, useAuth } from '../context/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Table, TableHeader, TableHead, TableRow, TableBody, TableCell } from './ui/table';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Loader2, RefreshCcw, Database, HardDriveDownload, Shield, Trash2, PlayCircle, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';

const statusColor: Record<string,string> = {
  PENDING: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  SUCCESS: 'bg-green-500/20 text-green-300 border-green-500/30',
  FAILED: 'bg-red-500/20 text-red-300 border-red-500/30'
};

const BackupPage: React.FC = () => {
  const { push } = useToast();
  const { hasPermission } = useAuth();
  const [backups, setBackups] = useState<BackupRecord[]>([]);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [typeSelect, setTypeSelect] = useState<'FULL'|'INCREMENTAL'|'FILES'|'DB'>('FULL');
  const [location, setLocation] = useState('');
  const [restoreModal, setRestoreModal] = useState<{ open: boolean; backup?: BackupRecord; mode: 'DRY' | 'APPLY' }>(() => ({ open: false, mode: 'DRY' }));
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [restoreResult, setRestoreResult] = useState<RestoreResult | null>(null);
  const [tablesFilter, setTablesFilter] = useState('');

  const canManage = hasPermission('system:backups');

  const fetchAll = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const list = await backupService.listBackups(page, size);
      setBackups(list.items);
      setTotal(list.total);
      try { const st = await backupService.getStats(); setStats(st); } catch {}
    } catch (e: any) {
      setError(e.message || 'Failed to load backups');
    } finally { setLoading(false); }
  }, [page, size]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const created = await backupService.createBackup(typeSelect, location || undefined);
      push({ type: 'success', title: 'Backup Started', message: `Type ${created.type}` });
      if (created?.id) setBackups(prev => [{...created}, ...prev]);
      fetchAll();
    } catch (e: any) {
      push({ type: 'error', title: 'Create Failed', message: e.message || 'Could not create backup' });
    } finally { setCreating(false); }
  };

  const handleDelete = async (b: BackupRecord) => {
    if (!window.confirm('Delete this backup?')) return;
    const prev = backups;
    setBackups(list => list.filter(x => x.id !== b.id));
    try {
      await backupService.deleteBackup(b.id);
      push({ type: 'success', message: 'Backup deleted' });
      setTotal(t => t - 1);
    } catch (e: any) {
      push({ type: 'error', title: 'Delete Failed', message: e.message || 'Could not delete' });
      setBackups(prev);
    }
  };

  const openRestore = (b: BackupRecord, mode: 'DRY' | 'APPLY') => {
    setRestoreResult(null);
    setRestoreModal({ open: true, backup: b, mode });
  };

  const executeRestore = async () => {
    if (!restoreModal.backup) return;
    setRestoreLoading(true); setRestoreResult(null);
    const tables = tablesFilter.split(',').map(t => t.trim()).filter(Boolean);
    try {
      const result = restoreModal.mode === 'DRY'
        ? await backupService.restoreDryRun(restoreModal.backup.id, tables.length ? tables : undefined)
        : await backupService.restoreApply(restoreModal.backup.id, tables.length ? tables : undefined);
      setRestoreResult(result);
  push({ type: 'success', title: restoreModal.mode === 'DRY' ? 'Dry Run Complete' : 'Restore Complete', message: (result && typeof result.message === 'string' ? result.message : 'Done') });
    } catch (e: any) {
      push({ type: 'error', title: 'Restore Failed', message: e.message || 'Could not restore' });
    } finally { setRestoreLoading(false); }
  };

  const totalPages = Math.max(1, Math.ceil(total / size));

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Backups</h1>
          <p className="text-white/60">Create, monitor and restore system backups</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10" onClick={fetchAll} disabled={loading}>
            <RefreshCcw className="w-4 h-4 mr-2" /> Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Existing Backups</CardTitle>
            </CardHeader>
            <CardContent>
              {error && <div className="mb-4 p-3 text-sm rounded border border-red-500/30 bg-red-500/10 text-red-300 flex items-start gap-2"><AlertTriangle className="w-4 h-4 mt-0.5" /> {error}</div>}
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">ID</TableHead>
                    <TableHead className="text-white/70">Type</TableHead>
                    <TableHead className="text-white/70">Status</TableHead>
                    <TableHead className="text-white/70">Size</TableHead>
                    <TableHead className="text-white/70">Created</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10"><TableCell colSpan={6} className="py-10 text-center text-white/60"><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Loading backups...</TableCell></TableRow>) }
                  {!loading && backups.length === 0 && (
                    <TableRow className="border-white/10"><TableCell colSpan={6} className="py-10 text-center text-white/60">No backups found</TableCell></TableRow>) }
                  {!loading && backups.map(b => (
                    <TableRow key={b.id} className="border-white/10 hover:bg-white/5">
                      <TableCell className="text-white/80 text-xs">{b.id}</TableCell>
                      <TableCell><Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 text-[10px]">{b.type}</Badge></TableCell>
                      <TableCell><Badge className={statusColor[b.status] || 'bg-white/10 text-white border-white/20 text-[10px]'}>{b.status}</Badge></TableCell>
                      <TableCell className="text-white/60 text-xs">{b.sizeMB ? `${b.sizeMB.toFixed(1)} MB` : '—'}</TableCell>
                      <TableCell className="text-white/60 text-xs">{new Date(b.createdAt).toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <PermissionGuard anyOf={['system:backups']} fallback={null}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => openRestore(b,'DRY')}><PlayCircle className="w-4 h-4" /></Button>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => openRestore(b,'APPLY')}><Database className="w-4 h-4" /></Button>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={() => handleDelete(b)}><Trash2 className="w-4 h-4" /></Button>
                          </PermissionGuard>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex items-center justify-between mt-4 text-white/60 text-xs">
                <div>Page {page} of {totalPages} • {total} total</div>
                <div className="flex gap-2 items-center">
                  <Button size="sm" variant="outline" disabled={page<=1 || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => setPage(p => Math.max(1, p-1))}>Prev</Button>
                  <Button size="sm" variant="outline" disabled={page>=totalPages || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => setPage(p => Math.min(totalPages, p+1))}>Next</Button>
                  <select value={size} onChange={e => { setSize(Number(e.target.value)); setPage(1); }} className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-[11px]">
                    {[10,20,50].map(s => <option key={s} value={s}>{s}/page</option>)}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader><CardTitle className="text-white flex items-center gap-2"><Shield className="w-4 h-4" />Create Backup</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {!canManage && <p className="text-white/60 text-sm">You lack permission to manage backups.</p>}
              {canManage && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[10px] uppercase text-white/50 mb-1">Type</label>
                      <select value={typeSelect} onChange={e => setTypeSelect(e.target.value as any)} className="w-full bg-white/10 border border-white/20 rounded px-2 py-2 text-white text-sm">
                        {['FULL','INCREMENTAL','FILES','DB'].map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] uppercase text-white/50 mb-1">Location (optional)</label>
                      <Input value={location} onChange={e => setLocation(e.target.value)} className="bg-white/10 border-white/20 text-white" placeholder="/path/or/uri" />
                    </div>
                  </div>
                  <Button disabled={creating} onClick={handleCreate} className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                    {creating && <Loader2 className="w-4 h-4 mr-2 animate-spin" />} Create Backup
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader><CardTitle className="text-white flex items-center gap-2"><HardDriveDownload className="w-4 h-4" />Statistics</CardTitle></CardHeader>
            <CardContent className="space-y-2 text-white/70 text-sm">
              {!stats && <p className="text-white/40 text-xs">No stats yet.</p>}
              {stats && (
                <ul className="space-y-1 text-xs">
                  <li>Total: <span className="text-white/90">{stats.total}</span></li>
                  <li>Successful: <span className="text-green-300">{stats.successful}</span></li>
                  <li>Failed: <span className="text-red-300">{stats.failed}</span></li>
                  <li>Pending: <span className="text-amber-300">{stats.pending}</span></li>
                  <li>Total Size: {stats.total_size_mb.toFixed(2)} MB</li>
                  <li>Last Backup: {stats.last_backup_at ? new Date(stats.last_backup_at).toLocaleString() : '—'}</li>
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {restoreModal.open && restoreModal.backup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-xl bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-white text-lg font-medium">{restoreModal.mode === 'DRY' ? 'Dry Run Restore' : 'Apply Restore'} • Backup #{restoreModal.backup.id}</h2>
              <button className="text-white/60 hover:text-white" onClick={() => setRestoreModal({ open: false, mode: 'DRY' })}>✕</button>
            </div>
            <div className="p-5 space-y-4 max-h-[70vh] overflow-y-auto text-sm">
              <div className="space-y-1">
                <p className="text-white/70 text-xs">Optionally restrict to comma-separated table names:</p>
                <Input value={tablesFilter} onChange={e => setTablesFilter(e.target.value)} placeholder="users,branches" className="bg-white/10 border-white/20 text-white" />
              </div>
              <Button disabled={restoreLoading} onClick={executeRestore} className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
                {restoreLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {restoreModal.mode === 'DRY' ? 'Execute Dry Run' : 'Apply Restore'}
              </Button>
              {restoreResult && (
                <div className="bg-white/5 border border-white/10 rounded p-3 space-y-2 text-white/70 text-xs">
                  <div className="flex items-center gap-2 text-white">
                    {restoreModal.mode === 'DRY' ? <Clock className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    <span className="font-medium">Result</span>
                  </div>
                  <pre className="whitespace-pre-wrap break-words max-h-60 overflow-y-auto">{JSON.stringify(restoreResult, null, 2)}</pre>
                </div>
              )}
            </div>
            <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
              <Button variant="ghost" className="text-white/70 hover:text-white" onClick={() => setRestoreModal({ open: false, mode: 'DRY' })}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackupPage;