import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { 
  FileText, 
  Search, 
  Download,
  Eye,
  Shield,
  User,
  Database,
  Settings,
  AlertTriangle,
  Loader2,
  Calendar,
  RefreshCcw,
  Activity
} from 'lucide-react';
import { auditService } from '../services/audit';
import type { AuditLog, AuditLogSeverity } from '../types';
import { useAuth } from '../context/AuthContext';

interface EnrichedAuditLog extends AuditLog {
  userDisplay?: string; // derive from user?.firstName
  entityDisplay?: string; // combination of entityType+entityId
  beforeJSON?: string;
  afterJSON?: string;
  severityNorm?: 'info' | 'medium' | 'high'; // map backend severities (INFO/WARNING/ERROR/CRITICAL)
}

export function AuditLogsPage() {
  const { hasPermission } = useAuth();
  const canView = hasPermission('audit:logs:view');
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState<string>('all');
  const [userIdMap, setUserIdMap] = useState<Record<string, number>>({});
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [logs, setLogs] = useState<EnrichedAuditLog[]>([]);
  const [selectedLog, setSelectedLog] = useState<EnrichedAuditLog | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const pollRef = React.useRef<number | null>(null);
  const debouncedRef = React.useRef<number | null>(null);

  const severityMap = (sev?: AuditLogSeverity): 'info' | 'medium' | 'high' => {
    switch (sev) {
      case 'INFO': return 'info';
      case 'WARNING': return 'medium';
      case 'ERROR':
      case 'CRITICAL': return 'high';
      default: return 'info';
    }
  };

  const fetchLogs = useCallback(async (override?: { page?: number; size?: number }) => {
    if (!canView) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await auditService.getAuditLogs({
        page: override?.page ?? page,
        size: override?.size ?? size,
        action: actionFilter !== 'all' ? actionFilter : undefined,
        severity: severityFilter !== 'all' ? (severityFilter.toUpperCase() as AuditLogSeverity) : undefined,
        fromDate: fromDate || undefined,
        toDate: toDate || undefined,
        userId: userFilter !== 'all' ? userIdMap[userFilter] : undefined
      });
      const enriched = resp.items
        .filter(l => {
          if (!searchTerm) return true;
          const term = searchTerm.toLowerCase();
            return (
              (l.action || '').toLowerCase().includes(term) ||
              (l.entityType || '').toLowerCase().includes(term) ||
              (l.user?.firstName || '').toLowerCase().includes(term) ||
              (l.user?.username || '').toLowerCase().includes(term) ||
              (l.oldValues ? JSON.stringify(l.oldValues).toLowerCase().includes(term) : false) ||
              (l.newValues ? JSON.stringify(l.newValues).toLowerCase().includes(term) : false)
            );
        })
        .map(l => ({
          ...l,
          userDisplay: l.user ? (l.user.firstName ? `${l.user.firstName} ${l.user.lastName}` : l.user.username) : 'System',
          entityDisplay: l.entityType ? `${l.entityType}:${l.entityId ?? ''}` : '—',
          beforeJSON: l.oldValues ? JSON.stringify(l.oldValues, null, 2) : undefined,
          afterJSON: l.newValues ? JSON.stringify(l.newValues, null, 2) : undefined,
          severityNorm: severityMap(l.severity as AuditLogSeverity)
        } as EnrichedAuditLog));
      setLogs(enriched);
  setTotal(resp.total);
      // build userId mapping cache
      const additions: Record<string, number> = {};
      enriched.forEach(l => { if (l.userDisplay && l.userId) additions[l.userDisplay] = l.userId; });
      if (Object.keys(additions).length) setUserIdMap(prev => ({ ...prev, ...additions }));
      if (!selectedLog && enriched.length) setSelectedLog(enriched[0]);
    } catch (e: any) {
      setError(e?.message || 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  }, [canView, page, size, actionFilter, severityFilter, fromDate, toDate, searchTerm, selectedLog, userFilter, userIdMap]);

  useEffect(() => { fetchLogs(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (debouncedRef.current) window.clearTimeout(debouncedRef.current);
    debouncedRef.current = window.setTimeout(() => { setPage(1); fetchLogs({ page:1 }); }, 350);
    return () => { if (debouncedRef.current) window.clearTimeout(debouncedRef.current); };
  }, [searchTerm, actionFilter, severityFilter, fromDate, toDate, fetchLogs]);

  // polling effect
  useEffect(() => {
    if (polling) {
      pollRef.current = window.setInterval(() => fetchLogs(), 5000);
    } else if (pollRef.current) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => { if (pollRef.current) window.clearInterval(pollRef.current); };
  }, [polling, fetchLogs]);

  const filteredLogs = logs; // server + client mix filtering applied

  const getSeverityColor = (severity: 'info' | 'medium' | 'high') => {
    switch (severity) {
      case 'info': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('User')) return User;
    if (action.includes('Sale') || action.includes('Payment')) return Database;
    if (action.includes('Login') || action.includes('Deleted')) return Shield;
    if (action.includes('Backup') || action.includes('System')) return Settings;
    return FileText;
  };

  const getInitials = (name: string) => name.split(' ').map(n => n[0]).join('').toUpperCase();
  const uniqueUsers = [...new Set(logs.map(l => l.userDisplay || 'System'))];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl flex items-center">
            <FileText className="w-6 h-6 mr-3" />
            Audit Logs
          </h1>
          <p className="text-white/70">Track all system activities and user actions</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant={polling ? 'default' : 'outline'}
            className={polling ? 'bg-green-500/20 text-green-300 border-green-500/30' : 'border-white/30 text-white hover:bg-white/10'}
            onClick={() => setPolling(p => !p)}
          >
            <Activity className="w-4 h-4 mr-2" /> {polling ? 'Live On' : 'Live Off'}
          </Button>
          <Button
            variant="outline"
            className="border-white/30 text-white hover:bg-white/10"
            onClick={() => { /* Placeholder export hook */ /* Potential endpoint: /audit/logs/export */ }}
          >
            <Download className="w-4 h-4 mr-2" /> Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-white/70 text-sm">Total Logs</p>
                <p className="text-white text-xl">{total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <User className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-white/70 text-sm">Active Users</p>
                <p className="text-white text-xl">{uniqueUsers.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-8 h-8 text-yellow-400" />
              <div>
                <p className="text-white/70 text-sm">High Severity</p>
                <p className="text-white text-xl">{logs.filter(log => log.severityNorm === 'high').length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-purple-400" />
              <div>
                <p className="text-white/70 text-sm">Security Events</p>
                <p className="text-white text-xl">{logs.filter(log => (log.action || '').includes('Login') || (log.action || '').includes('Deleted')).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Logs List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                  <Input
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <Select value={userFilter} onValueChange={(v) => { setUserFilter(v); setPage(1); fetchLogs({ page:1 }); }}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Filter by user" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Users</SelectItem>
                    {uniqueUsers.map(user => <SelectItem key={user} value={user}>{user}</SelectItem>)}
                  </SelectContent>
                </Select>
                <Select value={actionFilter} onValueChange={(v) => setActionFilter(v)}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Filter by action" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Actions</SelectItem>
                    <SelectItem value="User">User Actions</SelectItem>
                    <SelectItem value="Sale">Sales</SelectItem>
                    <SelectItem value="Login">Authentication</SelectItem>
                    <SelectItem value="System">System</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={severityFilter} onValueChange={(v) => setSeverityFilter(v)}>
                <div className="flex items-center space-x-2 md:col-span-2 lg:col-span-4">
                  <div className="flex items-center space-x-2 w-full">
                    <Calendar className="w-4 h-4 text-white/50" />
                    <Input
                      type="date"
                      value={fromDate}
                      onChange={e => setFromDate(e.target.value)}
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    />
                    <span className="text-white/50 text-xs">to</span>
                    <Input
                      type="date"
                      value={toDate}
                      onChange={e => setToDate(e.target.value)}
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                    />
                    <Button variant="ghost" size="sm" className="text-white/60 hover:text-white" onClick={() => { setFromDate(''); setToDate(''); }}>
                      <RefreshCcw className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Filter by severity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Severity</SelectItem>
                    <SelectItem value="info">Info</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Logs Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Activity Log</CardTitle>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="p-4 mb-4 bg-red-500/10 border border-red-500/20 rounded text-red-300 text-sm">
                  {error} <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={() => fetchLogs()}>Retry</Button>
                </div>
              )}
              {!canView && (
                <div className="p-8 text-center text-white/60 text-sm">
                  <Shield className="w-5 h-5 mx-auto mb-2 text-white/40" />
                  You don&apos;t have permission to view audit logs.
                </div>
              )}
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Timestamp</TableHead>
                    <TableHead className="text-white/70">User</TableHead>
                    <TableHead className="text-white/70">Action</TableHead>
                    <TableHead className="text-white/70">Severity</TableHead>
                    <TableHead className="text-white/70">Details</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={6} className="py-10 text-center text-white/60">
                        <Loader2 className="w-5 h-5 mr-2 inline animate-spin" /> Loading logs...
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredLogs.length === 0 && !error && canView && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={6} className="py-10 text-center text-white/60">
                        No logs found
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredLogs.map((log) => {
                    const ActionIcon = getActionIcon(log.action || '');
                    return (
                      <TableRow 
                        key={log.id} 
                        className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedLog?.id === log.id ? 'bg-white/10' : ''}`}
                        onClick={() => setSelectedLog(log)}
                      >
                        <TableCell className="text-white/70 text-sm">{log.createdAt?.replace('T',' ').slice(0,19) || '—'}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Avatar className="w-6 h-6">
                              <AvatarImage src="" />
                              <AvatarFallback className="bg-white/20 text-white text-xs">
                                {getInitials(log.userDisplay || 'S')}
                              </AvatarFallback>
                            </Avatar>
                            <span className="text-white text-sm">{log.userDisplay}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <ActionIcon className="w-4 h-4 text-white/70" />
                            <span className="text-white text-sm">{log.action || '—'}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getSeverityColor(log.severityNorm || 'info')}>
                            {log.severityNorm}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-white/70 text-sm max-w-xs truncate" title={(log.newValues ? JSON.stringify(log.newValues) : log.action) || ''}>
                          {(log.action || '') + (log.entityType ? ` (${log.entityType})` : '')}
                        </TableCell>
                        <TableCell>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
              {/* Pagination */}
              <div className="flex items-center justify-between mt-4 text-white/70 text-sm">
                <div>
                  Page {page} of {Math.max(1, Math.ceil(total / size))} • {total} total
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline" disabled={page <= 1 || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => { const newPage = page - 1; setPage(newPage); fetchLogs({ page: newPage }); }}>Prev</Button>
                  <Button size="sm" variant="outline" disabled={page >= Math.ceil(total / size) || loading} className="border-white/30 text-white/70 hover:text-white" onClick={() => { const newPage = page + 1; setPage(newPage); fetchLogs({ page: newPage }); }}>Next</Button>
                  <select value={size} onChange={e => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); fetchLogs({ page:1, size: newSize }); }} className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none">
                    {[25,50,100].map(s => <option key={s} value={s}>{s}/page</option>)}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Log Details */}
        <div className="space-y-4">
          {selectedLog ? (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Log Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="text-white">{selectedLog.action || '—'}</h3>
                    <Badge className={getSeverityColor(selectedLog.severityNorm || 'info')}>
                      {selectedLog.severityNorm}
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <p className="text-white/70 text-sm">User</p>
                      <div className="flex items-center space-x-2">
                        <Avatar className="w-6 h-6">
                          <AvatarImage src="" />
                          <AvatarFallback className="bg-white/20 text-white text-xs">
                            {getInitials(selectedLog.userDisplay || 'S')}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-white text-sm">{selectedLog.userDisplay}</span>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-white/70 text-sm">Timestamp</p>
                      <p className="text-white text-sm">{selectedLog.createdAt?.replace('T',' ').slice(0,19) || '—'}</p>
                    </div>
                    
                    <div>
                      <p className="text-white/70 text-sm">Entity</p>
                      <p className="text-white text-sm">{selectedLog.entityDisplay}</p>
                    </div>
                    
                    <div>
                      <p className="text-white/70 text-sm">IP Address</p>
                      <p className="text-white text-sm font-mono">{selectedLog.ipAddress || '—'}</p>
                    </div>
                    
                    <div>
                      <p className="text-white/70 text-sm">Details</p>
                      <p className="text-white text-sm">{selectedLog.action || '—'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              {(selectedLog.beforeJSON || selectedLog.afterJSON) && (
                <Card className="bg-white/10 backdrop-blur-md border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Data Changes</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <DiffViewer before={selectedLog.beforeJSON} after={selectedLog.afterJSON} />
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent>
                <p className="text-white/70">Select a log entry to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Lightweight diff viewer (line-level + inline char highlighting)
interface DiffViewerProps { before?: string; after?: string; }
function DiffViewer({ before, after }: DiffViewerProps) {
  if (!before && !after) return null;
  // Parse lines
  const beforeLines = before ? before.split('\n') : [];
  const afterLines = after ? after.split('\n') : [];
  const maxLen = Math.max(beforeLines.length, afterLines.length);
  const rows: Array<{ type: 'unchanged' | 'added' | 'removed' | 'modified'; before?: string; after?: string }> = [];
  for (let i = 0; i < maxLen; i++) {
    const b = beforeLines[i];
    const a = afterLines[i];
    if (b === a) {
      rows.push({ type: 'unchanged', before: b, after: a });
    } else if (b !== undefined && a === undefined) {
      rows.push({ type: 'removed', before: b });
    } else if (b === undefined && a !== undefined) {
      rows.push({ type: 'added', after: a });
    } else if (b !== a) {
      rows.push({ type: 'modified', before: b, after: a });
    }
  }

  const highlightChars = (oldStr = '', newStr = '') => {
    if (oldStr === newStr) return { oldFrag: oldStr, newFrag: newStr };
    // find first diff index
    let start = 0; while (start < oldStr.length && start < newStr.length && oldStr[start] === newStr[start]) start++;
    // find end diff index
    let endOld = oldStr.length - 1, endNew = newStr.length - 1;
    while (endOld >= start && endNew >= start && oldStr[endOld] === newStr[endNew]) { endOld--; endNew--; }
    return {
      oldFrag: (
        <>
          <span>{oldStr.slice(0,start)}</span>
          <span className="bg-red-500/30">{oldStr.slice(start, endOld+1)}</span>
          <span>{oldStr.slice(endOld+1)}</span>
        </>
      ),
      newFrag: (
        <>
          <span>{newStr.slice(0,start)}</span>
          <span className="bg-green-500/30">{newStr.slice(start, endNew+1)}</span>
          <span>{newStr.slice(endNew+1)}</span>
        </>
      )
    };
  };

  return (
    <div className="text-xs font-mono space-y-1">
      {rows.map((r, idx) => {
        if (r.type === 'unchanged') return (
          <div key={idx} className="flex gap-2 opacity-60">
            <div className="w-6 text-right select-none text-white/40">{idx+1}</div>
            <div className="flex-1 whitespace-pre overflow-x-auto">{r.before}</div>
          </div>
        );
        if (r.type === 'removed') return (
          <div key={idx} className="flex gap-2">
            <div className="w-6 text-right select-none text-red-400">{idx+1}</div>
            <div className="flex-1 whitespace-pre overflow-x-auto bg-red-500/10 text-red-300">{r.before}</div>
          </div>
        );
        if (r.type === 'added') return (
          <div key={idx} className="flex gap-2">
            <div className="w-6 text-right select-none text-green-400">{idx+1}</div>
            <div className="flex-1 whitespace-pre overflow-x-auto bg-green-500/10 text-green-300">{r.after}</div>
          </div>
        );
        // modified
        const { oldFrag, newFrag } = highlightChars(r.before || '', r.after || '');
        return (
          <div key={idx} className="space-y-0.5">
            <div className="flex gap-2">
              <div className="w-6 text-right select-none text-red-400">{idx+1}</div>
              <div className="flex-1 whitespace-pre overflow-x-auto bg-red-500/10 text-red-300">{oldFrag}</div>
            </div>
            <div className="flex gap-2">
              <div className="w-6 text-right select-none text-green-400">{idx+1}</div>
              <div className="flex-1 whitespace-pre overflow-x-auto bg-green-500/10 text-green-300">{newFrag}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}