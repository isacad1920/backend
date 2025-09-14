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
  currentPage: string;
  onPageChange: (page: string) => void;
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
  backup: ['system:backups'],
  settings: ['system:settings:view']
};

export function Sidebar({ currentPage, onPageChange, user, onLogout }: SidebarProps) {
  const { permissions } = useAuth();

  const filteredNavigation = useMemo(() => {
    if (permissions.includes('all')) return navigation;

    // Fallback: if permissions array is empty (session not enriched or legacy token),
    // expose a safe subset instead of ONLY dashboard to avoid UX dead-end.
    if (!permissions || permissions.length === 0) {
      const basicIds = new Set(['dashboard','pos','sales','inventory','customers']);
      return navigation.filter(n => !navPermissions[n.id] || basicIds.has(n.id));
    }

    return navigation.filter(item => {
      const req = navPermissions[item.id];
      if (!req) return true; // no permission mapping required
      const reqList = Array.isArray(req) ? req : [req];
      return reqList.some(r => permissions.includes(r));
    });
  }, [permissions]);

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
            const isActive = currentPage === item.id;
            
            return (
              <Button
                key={item.id}
                variant="ghost"
                className={`w-full justify-start text-left h-10 px-3 ${
                  isActive
                    ? 'bg-white/20 text-white border border-white/30'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
                onClick={() => onPageChange(item.id)}
              >
                <Icon className="w-4 h-4 mr-3" />
                <span className="flex-1">{item.label}</span>
                {isActive && <ChevronRight className="w-4 h-4" />}
              </Button>
            );
          })}
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