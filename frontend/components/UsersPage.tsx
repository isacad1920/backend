import React, { useState, useEffect, useCallback } from 'react';
import { useToast } from '../context/ToastContext';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { 
  Plus, 
  Search, 
  Shield,
  Edit,
  Trash2,
  UserCheck,
  UserX,
  Settings,
  Loader2,
  X,
  AlertTriangle
} from 'lucide-react';
import { usersService } from '../services/users';
import { branchesService } from '../services/branches';
import { Role, type User } from '../types';
import { useAuth, PermissionGuard } from '../context/AuthContext';

// Role color mapping (match backend enum Role names)
const roleColors: Record<string, string> = {
  ADMIN: 'bg-red-500/20 text-red-400 border-red-500/30',
  MANAGER: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  CASHIER: 'bg-green-500/20 text-green-400 border-green-500/30',
  ACCOUNTANT: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  INVENTORY_CLERK: 'bg-amber-500/20 text-amber-400 border-amber-500/30'
};

interface EnrichedUser extends User {
  // Placeholder analytics until backend endpoints provided
  lastLogin?: string;
  permissionCount?: number; // derived from permissions list if we fetch later
  branchName?: string; // if backend expands with branch relation
  status?: 'active' | 'inactive'; // map from isActive
  permissions?: string[]; // if later extended via separate endpoint
}

export function UsersPage() {
  const { push } = useToast();
  const { hasPermission } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | Role>('all');
  const [branchFilter, setBranchFilter] = useState<number | 'all'>('all');
  const [users, setUsers] = useState<EnrichedUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<EnrichedUser | null>(null);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [branches, setBranches] = useState<Array<{ id: number; name: string }>>([]);
  const [branchLoading, setBranchLoading] = useState(false);

  // Create user modal state
  const [showCreate, setShowCreate] = useState(false);
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [newUserData, setNewUserData] = useState<{ username: string; email: string; firstName: string; lastName: string; role: Role; branchId?: number; password: string }>({
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    role: Role.CASHIER,
    branchId: undefined,
    password: ''
  });
  const [createTouched, setCreateTouched] = useState<Record<string, boolean>>({});
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const createValidation = () => {
    const errors: Record<string,string> = {};
    if (!newUserData.username.trim()) errors.username = 'Username is required';
    if (!newUserData.email.trim()) errors.email = 'Email is required';
    else if (!emailRegex.test(newUserData.email.trim())) errors.email = 'Invalid email format';
    if (!newUserData.firstName.trim()) errors.firstName = 'First name required';
    if (!newUserData.lastName.trim()) errors.lastName = 'Last name required';
    if (!newUserData.password.trim()) errors.password = 'Password required';
    else if (newUserData.password.trim().length < 6) errors.password = 'Min 6 characters';
    return errors;
  };
  const debouncedRef = React.useRef<number | null>(null);

  const fetchUsers = useCallback(async (override?: { page?: number; size?: number; term?: string; role?: Role | 'all'; branchId?: number | 'all' }) => {
    if (!hasPermission('users:view')) return;
    setLoading(true);
    setError(null);
    try {
      const term = override?.term ?? searchTerm;
      const role = override?.role ?? roleFilter;
      const branchId = override?.branchId ?? branchFilter;
      const resp = await usersService.getUsers({
        page: override?.page ?? page,
        size: override?.size ?? size,
        q: term ? term : undefined,
        role: role !== 'all' ? role : undefined,
        branchId: branchId !== 'all' ? Number(branchId) : undefined
      });
      const enriched = resp.items.map(u => ({
        ...u,
        status: u.isActive ? 'active' : 'inactive',
        permissionCount: (u as any).permissions ? (u as any).permissions.length : undefined
      } as EnrichedUser));
      setUsers(enriched);
      setTotal(resp.pagination.total);
      if (!selectedUser && enriched.length > 0) setSelectedUser(enriched[0]);
    } catch (e: any) {
      setError(e?.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [page, size, roleFilter, branchFilter, searchTerm, hasPermission, selectedUser]);

  useEffect(() => { fetchUsers(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (debouncedRef.current) window.clearTimeout(debouncedRef.current);
    debouncedRef.current = window.setTimeout(() => { setPage(1); fetchUsers({ page: 1 }); }, 300);
    return () => { if (debouncedRef.current) window.clearTimeout(debouncedRef.current); };
  }, [searchTerm, roleFilter, branchFilter, fetchUsers]);

  // Load branches for filter
  useEffect(() => {
    let active = true;
    if (!hasPermission('branches:view')) return; // optional guard
    (async () => {
      setBranchLoading(true);
      try {
        const resp = await branchesService.getBranches({ page: 1, size: 50 });
        if (active) setBranches(resp.items.map(b => ({ id: b.id, name: b.name })));
      } catch (e) {
        // silent fail, we can still render users
      } finally {
        if (active) setBranchLoading(false);
      }
    })();
    return () => { active = false; };
  }, [hasPermission]);

  const filteredUsers = users; // server-side filtering applied

  const getRoleColor = (role: string) => roleColors[role] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  const getStatusColor = (status: string) => status === 'active' ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  const getInitials = (nameOrEmail: string) => nameOrEmail.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase();

  const canCreate = hasPermission('users:create');
  const canView = hasPermission('users:view');
  const canToggle = hasPermission('users:deactivate') || hasPermission('users:activate');
  const canDelete = hasPermission('users:delete');

  const [permissionsLoading, setPermissionsLoading] = useState(false);
  const [showAllPermissions, setShowAllPermissions] = useState(false);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canCreate) return;
    const errs = createValidation();
    if (Object.keys(errs).length) {
      setCreateTouched({ username: true, email: true, firstName: true, lastName: true, role: true, password: true });
      return;
    }
    setCreateSubmitting(true);
    setCreateError(null);
    try {
      const payload = {
        username: newUserData.username.trim(),
        email: newUserData.email.trim(),
        firstName: newUserData.firstName.trim(),
        lastName: newUserData.lastName.trim(),
        role: newUserData.role,
        branchId: newUserData.branchId || undefined,
        password: newUserData.password // backend expects raw password per schema
      } as any;
      const optimistic: EnrichedUser = {
        id: Date.now() * -1, // temporary negative id
        username: payload.username,
        email: payload.email,
        firstName: payload.firstName,
        lastName: payload.lastName,
        role: payload.role,
        branchId: payload.branchId,
        isActive: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        status: 'active'
      } as EnrichedUser;
      setUsers(prev => [optimistic, ...prev]);
      // Fire real request
      const created = await usersService.createUser(payload);
      setUsers(prev => prev.map(u => u.id === optimistic.id ? { ...optimistic, ...created } : u));
      setSelectedUser(created as EnrichedUser);
      setShowCreate(false);
      // refresh total count
      fetchUsers();
      push({ type: 'success', title: 'User Created', message: `User ${payload.username || payload.email} created.` });
    } catch (err: any) {
      setUsers(prev => prev.filter(u => u.id >= 0)); // remove optimistic on failure
      setCreateError(err?.message || 'Failed to create user');
      push({ type: 'error', title: 'Create Failed', message: err?.message || 'Failed to create user' });
    } finally {
      setCreateSubmitting(false);
    }
  };

  const createErrors = createValidation();
  const showError = (field: string) => createTouched[field] && createErrors[field];

  const toggleUserActive = async (user: EnrichedUser) => {
    if (!canToggle) return;
    const updated = { ...user, isActive: !user.isActive, status: !user.isActive ? 'active' : 'inactive' } as EnrichedUser;
    setUsers(prev => prev.map(u => u.id === user.id ? updated : u));
    if (selectedUser?.id === user.id) setSelectedUser(updated);
    try {
      await usersService.updateUser(user.id, { isActive: updated.isActive } as any);
      push({ type: 'success', message: `User ${user.username || user.email} ${updated.isActive ? 'activated' : 'deactivated'}.` });
    } catch (err) {
      // revert
      setUsers(prev => prev.map(u => u.id === user.id ? user : u));
      if (selectedUser?.id === user.id) setSelectedUser(user);
      push({ type: 'error', title: 'Action Failed', message: 'Could not update status.' });
    }
  };

  const deleteUser = async (user: EnrichedUser) => {
    if (!canDelete) return;
    if (!window.confirm(`Delete user ${user.username || user.email}? This cannot be undone.`)) return;
    const prev = users;
    setUsers(prevList => prevList.filter(u => u.id !== user.id));
    if (selectedUser?.id === user.id) setSelectedUser(null);
    try {
      await usersService.deleteUser(user.id);
      setTotal(t => t - 1);
      push({ type: 'success', message: `Deleted user ${user.username || user.email}` });
    } catch (err) {
      // revert
      setUsers(prev);
      if (!selectedUser) setSelectedUser(user);
      push({ type: 'error', title: 'Delete Failed', message: 'User could not be deleted.' });
    }
  };

  // Fetch per-user permissions when selecting a user without loaded permissions
  useEffect(() => {
    let active = true;
    (async () => {
      if (!selectedUser) return;
      if ((selectedUser as any).permissions && (selectedUser as any).permissions.length) return;
      if (!hasPermission('users:view')) return;
      setPermissionsLoading(true);
      try {
        if ((usersService as any).getUserPermissions) {
          const perms = await (usersService as any).getUserPermissions(selectedUser.id);
          if (active) {
            setSelectedUser(su => su && su.id === selectedUser.id ? { ...su, permissions: perms, permissionCount: perms.length } : su);
            setUsers(prev => prev.map(u => u.id === selectedUser.id ? { ...u, permissions: perms, permissionCount: perms.length } as EnrichedUser : u));
          }
        }
      } catch (e) {
        // silent fail, keep placeholder count
      } finally {
        if (active) setPermissionsLoading(false);
      }
    })();
    return () => { active = false; };
  }, [selectedUser, hasPermission]);

  return (
    <>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Users & Permissions</h1>
          <p className="text-white/70">Manage user accounts and access permissions</p>
        </div>
        <div className="flex space-x-2">
          <PermissionGuard anyOf={['users:create']} fallback={null}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30" onClick={() => setShowCreate(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add User
            </Button>
          </PermissionGuard>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Settings className="w-4 h-4 mr-2" />
            Bulk Actions
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Filters */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                  <Input
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <div className="flex space-x-2 items-center">
                  {['all','ADMIN','MANAGER','CASHIER','ACCOUNTANT','INVENTORY_CLERK'].map(role => (
                    <Button
                      key={role}
                      variant={roleFilter === role ? 'default' : 'outline'}
                      size="sm"
                      className={roleFilter === role ? 'bg-white/20 text-white border-white/30' : 'border-white/30 text-white hover:bg-white/10'}
                      onClick={() => { setRoleFilter(role as any); fetchUsers({ page:1, role: role as any }); setPage(1); }}
                    >
                      {role === 'all' ? 'All' : role.replace('_',' ')}
                    </Button>
                  ))}
                  <div className="ml-2">
                    <select
                      value={branchFilter}
                      onChange={(e) => { const val = e.target.value === 'all' ? 'all' : Number(e.target.value); setBranchFilter(val); setPage(1); fetchUsers({ page:1, branchId: val }); }}
                      className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none"
                    >
                      <option value="all">All Branches</option>
                      {branches.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                    </select>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* User Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">User List</CardTitle>
            </CardHeader>
            <CardContent>
              {!canView && (
                <div className="p-6 text-center text-white/60 text-sm">
                  <Shield className="w-5 h-5 mx-auto mb-2 text-white/40" />
                  You don't have permission to view users.
                </div>
              )}
              {error && (
                <div className="p-4 mb-4 bg-red-500/10 border border-red-500/20 rounded text-red-300 text-sm">
                  {error} <Button variant="ghost" size="sm" className="ml-2 text-red-200 hover:text-white" onClick={() => fetchUsers()}>Retry</Button>
                </div>
              )}
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">User</TableHead>
                    <TableHead className="text-white/70">Role</TableHead>
                    <TableHead className="text-white/70">Branch</TableHead>
                    <TableHead className="text-white/70">Status</TableHead>
                    <TableHead className="text-white/70">Permissions</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={6} className="py-10 text-center text-white/60">
                        <Loader2 className="w-5 h-5 mr-2 inline animate-spin" /> Loading users...
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredUsers.length === 0 && !error && canView && (
                    <TableRow className="border-white/10">
                      <TableCell colSpan={6} className="py-10 text-center text-white/60">
                        No users found
                      </TableCell>
                    </TableRow>
                  )}
                  {!loading && filteredUsers.map((user) => (
                    <TableRow
                      key={user.id}
                      className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedUser?.id === user.id ? 'bg-white/10' : ''}`}
                      onClick={() => setSelectedUser(user)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src="" />
                            <AvatarFallback className="bg-white/20 text-white text-xs">
                              {getInitials(user.firstName || user.username || user.email)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="text-white text-sm">{user.firstName ? `${user.firstName} ${user.lastName}` : user.username}</p>
                            <p className="text-white/70 text-xs">{user.email}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getRoleColor(user.role)}>{user.role}</Badge>
                      </TableCell>
                      <TableCell className="text-white/70">{(user as any).branchName || user.branchId || '—'}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(user.status || (user.isActive ? 'active':'inactive'))}>
                          {user.status || (user.isActive ? 'active':'inactive')}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white/70 text-xs">{user.permissionCount ?? '—'}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <PermissionGuard anyOf={['users:update']} fallback={null}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </PermissionGuard>
                          <PermissionGuard anyOf={['users:deactivate','users:activate']} fallback={null}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e) => { e.stopPropagation(); toggleUserActive(user); }}>
                              {user.isActive ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                            </Button>
                          </PermissionGuard>
                          <PermissionGuard anyOf={['users:delete']} fallback={null}>
                            <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10" onClick={(e) => { e.stopPropagation(); deleteUser(user); }}>
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </PermissionGuard>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {/* Pagination */}
              <div className="flex items-center justify-between mt-4 text-white/70 text-sm">
                <div>
                  Page {page} of {Math.max(1, Math.ceil(total / size))} • {total} total
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page <= 1 || loading}
                    className="border-white/30 text-white/70 hover:text-white"
                    onClick={() => { const newPage = page - 1; setPage(newPage); fetchUsers({ page: newPage }); }}
                  >Prev</Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={page >= Math.ceil(total / size) || loading}
                    className="border-white/30 text-white/70 hover:text-white"
                    onClick={() => { const newPage = page + 1; setPage(newPage); fetchUsers({ page: newPage }); }}
                  >Next</Button>
                  <select
                    value={size}
                    onChange={(e) => { const newSize = Number(e.target.value); setSize(newSize); setPage(1); fetchUsers({ page:1, size: newSize }); }}
                    className="bg-white/10 border border-white/20 rounded px-2 py-1 text-white text-xs focus:outline-none"
                  >
                    {[10,25,50].map(s => <option key={s} value={s}>{s}/page</option>)}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* User Details */}
        <div className="space-y-4">
          {selectedUser ? (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">User Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src="" />
                      <AvatarFallback className="bg-white/20 text-white">
                        {getInitials(selectedUser.firstName || selectedUser.username || selectedUser.email)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="text-white">{selectedUser.firstName ? `${selectedUser.firstName} ${selectedUser.lastName}` : selectedUser.username}</h3>
                      <p className="text-white/70 text-sm">{selectedUser.email}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Role</span>
                      <Badge className={getRoleColor(selectedUser.role)}>{selectedUser.role}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Branch</span>
                      <span className="text-white text-sm">{(selectedUser as any).branchName || selectedUser.branchId || '—'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Status</span>
                      <Badge className={getStatusColor(selectedUser.status || (selectedUser.isActive ? 'active':'inactive'))}>{selectedUser.status || (selectedUser.isActive ? 'active':'inactive')}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Permission Count</span>
                      <span className="text-white/70 text-sm">{selectedUser.permissionCount ?? '—'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Shield className="w-4 h-4 mr-2" />
                    Permissions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {permissionsLoading && (
                    <div className="text-white/60 text-sm">Loading permissions...</div>
                  )}
                  {!permissionsLoading && selectedUser.permissions && selectedUser.permissions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {(showAllPermissions ? selectedUser.permissions : selectedUser.permissions.slice(0,30)).map(p => (
                        <Badge key={p} className="bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-normal">
                          {p}
                        </Badge>
                      ))}
                      {selectedUser.permissions.length > 30 && !showAllPermissions && (
                        <button type="button" onClick={() => setShowAllPermissions(true)} className="text-[11px] text-white/60 underline ml-1">Show all ({selectedUser.permissions.length})</button>
                      )}
                      {showAllPermissions && selectedUser.permissions.length > 30 && (
                        <button type="button" onClick={() => setShowAllPermissions(false)} className="text-[11px] text-white/60 underline ml-1">Collapse</button>
                      )}
                    </div>
                  )}
                  {!permissionsLoading && (!selectedUser.permissions || selectedUser.permissions.length === 0) && (
                    <p className="text-white/60 text-sm">No permissions data available.</p>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <PermissionGuard anyOf={['users:update']} fallback={null}>
                    <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                      <Edit className="w-4 h-4 mr-2" />
                      Edit User (Soon)
                    </Button>
                  </PermissionGuard>
                  <PermissionGuard anyOf={['users:update']} fallback={null}>
                    <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                      <Shield className="w-4 h-4 mr-2" />
                      Manage Permissions (Soon)
                    </Button>
                  </PermissionGuard>
                  <PermissionGuard anyOf={['users:deactivate','users:activate']} fallback={null}>
                    <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10" onClick={() => toggleUserActive(selectedUser)}>
                      {selectedUser.isActive ? (
                        <>
                          <UserX className="w-4 h-4 mr-2" />
                          Deactivate
                        </>
                      ) : (
                        <>
                          <UserCheck className="w-4 h-4 mr-2" />
                          Activate
                        </>
                      )}
                    </Button>
                  </PermissionGuard>
                  <PermissionGuard anyOf={['users:delete']} fallback={null}>
                    <Button variant="destructive" className="w-full bg-red-500/20 hover:bg-red-500/30 text-red-200 border border-red-500/30" onClick={() => deleteUser(selectedUser)}>
                      <Trash2 className="w-4 h-4 mr-2" /> Delete User
                    </Button>
                  </PermissionGuard>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-8 text-center text-white/60 text-sm">Select a user to view details</CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
    {showCreate && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
        <div className="w-full max-w-lg bg-zinc-900 border border-white/20 rounded-lg shadow-xl overflow-hidden animate-in fade-in zoom-in">
          <form onSubmit={handleCreateUser} className="flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
              <h2 className="text-white text-lg font-medium">Create User</h2>
              <button type="button" onClick={() => setShowCreate(false)} className="text-white/60 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="px-5 py-4 space-y-4 overflow-y-auto">
              {createError && (
                <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-sm p-2 rounded flex items-start">
                  <AlertTriangle className="w-4 h-4 mr-2 mt-0.5" /> {createError}
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Username<span className="text-red-400">*</span></label>
                  <Input
                    value={newUserData.username}
                    onChange={e => { setNewUserData(d => ({ ...d, username: e.target.value })); }}
                    onBlur={() => setCreateTouched(t => ({ ...t, username: true }))}
                    className={`bg-white/10 border ${showError('username') ? 'border-red-500/60' : 'border-white/20'} text-white`}
                    placeholder="jdoe"
                  />
                  {showError('username') && <p className="text-red-400 text-[11px] mt-1">{createErrors.username}</p>}
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Email<span className="text-red-400">*</span></label>
                  <Input
                    value={newUserData.email}
                    onChange={e => { setNewUserData(d => ({ ...d, email: e.target.value })); }}
                    onBlur={() => setCreateTouched(t => ({ ...t, email: true }))}
                    className={`bg-white/10 border ${showError('email') ? 'border-red-500/60' : 'border-white/20'} text-white`}
                    placeholder="user@example.com"
                  />
                  {showError('email') && <p className="text-red-400 text-[11px] mt-1">{createErrors.email}</p>}
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">First Name<span className="text-red-400">*</span></label>
                  <Input
                    value={newUserData.firstName}
                    onChange={e => { setNewUserData(d => ({ ...d, firstName: e.target.value })); }}
                    onBlur={() => setCreateTouched(t => ({ ...t, firstName: true }))}
                    className={`bg-white/10 border ${showError('firstName') ? 'border-red-500/60' : 'border-white/20'} text-white`}
                    placeholder="John"
                  />
                  {showError('firstName') && <p className="text-red-400 text-[11px] mt-1">{createErrors.firstName}</p>}
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Last Name<span className="text-red-400">*</span></label>
                  <Input
                    value={newUserData.lastName}
                    onChange={e => { setNewUserData(d => ({ ...d, lastName: e.target.value })); }}
                    onBlur={() => setCreateTouched(t => ({ ...t, lastName: true }))}
                    className={`bg-white/10 border ${showError('lastName') ? 'border-red-500/60' : 'border-white/20'} text-white`}
                    placeholder="Doe"
                  />
                  {showError('lastName') && <p className="text-red-400 text-[11px] mt-1">{createErrors.lastName}</p>}
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Role</label>
                  <select
                    value={newUserData.role}
                    onChange={e => setNewUserData(d => ({ ...d, role: e.target.value as Role }))}
                    className="w-full bg-white/10 border border-white/20 rounded px-2 py-2 text-white text-sm"
                  >
                    {['ADMIN','MANAGER','CASHIER','ACCOUNTANT','INVENTORY_CLERK'].map(r => <option key={r} value={r}>{r.replace('_',' ')}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Branch</label>
                  <select
                    value={newUserData.branchId ?? ''}
                    onChange={e => setNewUserData(d => ({ ...d, branchId: e.target.value ? Number(e.target.value) : undefined }))}
                    className="w-full bg-white/10 border border-white/20 rounded px-2 py-2 text-white text-sm"
                  >
                    <option value="">Unassigned</option>
                    {branches.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs uppercase tracking-wide text-white/60 mb-1">Password<span className="text-red-400">*</span></label>
                  <Input
                    type="password"
                    value={newUserData.password}
                    onChange={e => { setNewUserData(d => ({ ...d, password: e.target.value })); }}
                    onBlur={() => setCreateTouched(t => ({ ...t, password: true }))}
                    className={`bg-white/10 border ${showError('password') ? 'border-red-500/60' : 'border-white/20'} text-white`}
                    placeholder="••••••"
                  />
                  {showError('password') && <p className="text-red-400 text-[11px] mt-1">{createErrors.password}</p>}
                </div>
              </div>
              <p className="text-[11px] text-white/40">Fields marked * are required. Data validates client-side before submission.</p>
            </div>
            <div className="px-5 py-4 border-t border-white/10 flex items-center justify-end gap-2 bg-white/5">
              <Button type="button" variant="ghost" className="text-white/70 hover:text-white" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button
                type="submit"
                disabled={createSubmitting || Object.keys(createErrors).length > 0}
                className="bg-white/20 hover:bg-white/30 text-white border border-white/30 disabled:opacity-50"
              >
                {createSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Create User
              </Button>
            </div>
          </form>
        </div>
      </div>
    )}
    </>
  );
}