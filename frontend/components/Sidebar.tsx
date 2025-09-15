import React, { useMemo } from 'react';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Users,
  Building2,
  Tag,
  UserCog,
  BookOpen,
  Bell,
  Settings,
  Database,
  FileText,
  BarChart3,
  CreditCard,
  LogOut,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { usePermissions } from '../context/PermissionsContext';

interface UserInfo {
  name?: string;
  role?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigation: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'pos', label: 'Point of Sale', icon: CreditCard },
  { id: 'sales', label: 'Sales', icon: ShoppingCart },
  { id: 'inventory', label: 'Inventory', icon: Package },
  { id: 'products', label: 'Products', icon: Package },
  { id: 'customers', label: 'Customers', icon: Users },
  { id: 'branches', label: 'Branches', icon: Building2 },
  { id: 'categories', label: 'Categories', icon: Tag },
  { id: 'users', label: 'Users & Permissions', icon: UserCog },
  { id: 'journal', label: 'Journal & Accounting', icon: BookOpen },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'reports', label: 'Reports', icon: BarChart3 },
  { id: 'audit', label: 'Audit Logs', icon: FileText },
  { id: 'backup', label: 'Backup & Restore', icon: Database },
  { id: 'settings', label: 'System Settings', icon: Settings },
];

interface SidebarProps {
  user?: UserInfo | null;
  onLogout?: () => void;
}

// Mapping nav items to hypothetical permission codes (can be aligned with backend list)
// Map each nav id to one or more permission codes required to display it.
// NOTE: If the backend returns an empty permission array (e.g. legacy session format
// or permissions still loading), we provide a conservative fallback below so the
// user isn't locked into only the Dashboard view.
const navPermissions: Record<string, string | string[]> = {
  pos: 'pos:access',
  sales: ['sales:view', 'sales:list'],
  inventory: ['inventory:view', 'inventory:list'],
  products: ['products:view', 'inventory:view'],
  customers: ['customers:view'],
  branches: ['branches:view'],
  categories: ['products:categories:view'],
  users: ['users:view', 'permissions:view'],
  journal: ['journal:view'],
  notifications: ['notifications:view'],
  reports: ['reports:view'],
  audit: ['audit:view'],
  // Backend pages reference 'system:backups' elsewhere, align naming here
  backup: ['system:backups','system:backup'],
  settings: ['system:settings:view']
};

import { useLocation, useNavigate } from 'react-router-dom';

export function Sidebar({ user, onLogout }: SidebarProps) {
  const { permissions, loading: permsLoading } = usePermissions();
  const location = useLocation();
  const navigate = useNavigate();

  const activeId = React.useMemo(() => {
    const seg = location.pathname.split('/')[1];
    if (!seg) return 'dashboard';
    return seg;
  }, [location.pathname]);

  const filteredNavigation = useMemo(() => {
    // ADMIN / superuser detection: unified 'all' code or explicit role on user prop
    if (permissions.includes('all') || (user?.role || '').toLowerCase() === 'admin') return navigation;

    if (import.meta.env.DEV) {
      console.debug('[Sidebar] permissions (PermissionsContext) ->', permissions);
    }

    // While permissions loading or empty provide permissive list to avoid trapping user
    if (permsLoading || !permissions || permissions.length === 0) {
      const permissiveIds = new Set(navigation.map(n => n.id)); // show EVERYTHING while loading
      if (import.meta.env.DEV) console.debug('[Sidebar] permissive display (loading/empty)');
      return navigation.filter(n => permissiveIds.has(n.id));
    }

    // If suspiciously small list (<=3) treat as partial fetch -> show all but log diagnostic
    if (permissions.length <= 3 && !permissions.includes('all')) {
      if (import.meta.env.DEV) console.debug('[Sidebar] small permission set fallback -> showing full nav');
      return navigation;
    }

    const included: string[] = [];
    const excludedDebug: { id: string; required: string[] }[] = [];
    const result = navigation.filter(item => {
      const req = navPermissions[item.id];
      if (!req) { included.push(item.id); return true; }
      const reqList = Array.isArray(req) ? req : [req];
      const allow = reqList.some(r => permissions.includes(r));
      if (allow) included.push(item.id); else excludedDebug.push({ id: item.id, required: reqList });
      return allow;
    });
    if (import.meta.env.DEV) {
      console.debug('[Sidebar] included ->', included);
      if (excludedDebug.length) console.debug('[Sidebar] excluded ->', excludedDebug);
    }
    return result;
  }, [permissions, permsLoading, user?.role]);

  return (
    <div className="w-64 h-full bg-white/10 backdrop-blur-md border-r border-white/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/20">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-8 h-8 bg-white/20 rounded-lg">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-white">FinanceOS</h2>
            <p className="text-white/70 text-sm">v2.1.0</p>
          </div>
        </div>
      </div>

      {/* User Profile */}
      <div className="p-4 border-b border-white/20">
        <div className="flex items-center space-x-3">
          <Avatar className="w-10 h-10">
            <AvatarImage src="" />
            <AvatarFallback className="bg-white/20 text-white">
              {user?.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm truncate">{user?.name || 'User'}</p>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="bg-white/20 text-white text-xs">
                {user?.role || 'Admin'}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {filteredNavigation.map((item) => {
            const Icon = item.icon;
            const isActive = activeId === item.id;
            return (
              <Button
                key={item.id}
                variant="ghost"
                className={`w-full justify-start text-left h-10 px-3 ${
                  isActive
                    ? 'bg-white/20 text-white border border-white/30'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
                onClick={() => navigate(item.id === 'dashboard' ? '/dashboard' : `/${item.id}`)}
              >
                <Icon className="w-4 h-4 mr-3" />
                <span className="flex-1">{item.label}</span>
                {isActive && <ChevronRight className="w-4 h-4" />}
              </Button>
            );
          })}
          {filteredNavigation.length < navigation.length && (
            <div className="mt-4 text-[10px] text-white/40 px-2">
              Some pages hidden based on current permissions.
            </div>
          )}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/20">
        <Button
          variant="ghost"
          className="w-full justify-start text-white/70 hover:text-white hover:bg-white/10"
          onClick={onLogout}
        >
          <LogOut className="w-4 h-4 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );
}