import React, { useState } from 'react';
import { LoginPage } from './components/LoginPage';
import { Dashboard } from './components/Dashboard';
import { SalesPage } from './components/SalesPage';
import { InventoryPage } from './components/InventoryPage';
import { ProductsPage } from './components/ProductsPage';
import { CustomersPage } from './components/CustomersPage';
import { BranchesPage } from './components/BranchesPage';
import { CategoriesPage } from './components/CategoriesPage';
import { UsersPage } from './components/UsersPage';
import { JournalPage } from './components/JournalPage';
import { NotificationsPage } from './components/NotificationsPage';
import { SettingsPage } from './components/SettingsPage';
import BackupPage from './components/BackupPage';
import { AuditLogsPage } from './components/AuditLogsPage';
import { ReportsPage } from './components/ReportsPage';
import { POSPage } from './components/POSPage';
import { Sidebar } from './components/Sidebar';
import { Toaster } from './components/ui/sonner';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

function AppShell() {
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'sales':
        return <SalesPage />;
      case 'inventory':
        return <InventoryPage />;
      case 'products':
        return <ProductsPage />;
      case 'customers':
        return <CustomersPage />;
      case 'branches':
        return <BranchesPage />;
      case 'categories':
        return <CategoriesPage />;
      case 'users':
        return <UsersPage />;
      case 'journal':
        return <JournalPage />;
      case 'notifications':
        return <NotificationsPage />;
      case 'settings':
        return <SettingsPage />;
      case 'backup':
        return <BackupPage />;
      case 'audit':
        return <AuditLogsPage />;
      case 'reports':
        return <ReportsPage />;
      case 'pos':
        return <POSPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="flex h-screen">
        <Sidebar
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          user={{ name: user?.firstName + ' ' + user?.lastName, role: user?.role }}
          onLogout={logout}
        />
        <main className="flex-1 overflow-auto">
          <div className="min-h-full">
            {renderPage()}
          </div>
        </main>
      </div>
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <AppShell />
      </CartProvider>
    </AuthProvider>
  );
}