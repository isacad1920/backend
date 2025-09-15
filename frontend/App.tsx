import React from 'react';
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
import { PermissionsProvider } from './context/PermissionsContext';
import { CartProvider } from './context/CartContext';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { ToastProvider } from './context/ToastContext';
import { ErrorBoundaryProvider } from './context/ErrorBoundaryContext';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import ReactLazy = React.LazyExoticComponent;

const ReactQueryDevtoolsLazy: ReactLazy<any> | null = ((): ReactLazy<any> | null => {
  // Vite provides import.meta.env.DEV typing when tsconfig includes vite/client types
  // If not present yet, consider adding "/// <reference types=\"vite/client\" />" in a global d.ts
  if ((import.meta as any).env?.DEV) {
    return React.lazy(() => import('@tanstack/react-query-devtools').then(m => ({ default: (m as any).ReactQueryDevtools })));
  }
  return null;
})();

function ProtectedLayout() {
  const { isAuthenticated, user, logout } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="flex h-screen">
        <Sidebar user={{ name: user?.firstName + ' ' + user?.lastName, role: user?.role }} onLogout={logout} />
        <main className="flex-1 overflow-auto">
          <div className="min-h-full p-2 sm:p-4">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/pos" element={<POSPage />} />
              <Route path="/sales" element={<SalesPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/customers" element={<CustomersPage />} />
              <Route path="/branches" element={<BranchesPage />} />
              <Route path="/categories" element={<CategoriesPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/journal" element={<JournalPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/backup" element={<BackupPage />} />
              <Route path="/audit" element={<AuditLogsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </main>
      </div>
      <Toaster />
    </div>
  );
}

// Ensures that if a user manually visits /login while already authenticated, they are redirected.
function LoginGate() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (isAuthenticated) {
    // Preserve any redirect param in future (not implemented) — for now send to dashboard
    return <Navigate to="/dashboard" replace state={{ from: location }} />;
  }
  return <LoginPage />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <ErrorBoundaryProvider>
          <AuthProvider>
            <PermissionsProvider>
              <CartProvider>
                <BrowserRouter>
                  <Routes>
                    <Route path="/login" element={<LoginGate />} />
                    <Route path="/*" element={<ProtectedLayout />} />
                  </Routes>
                </BrowserRouter>
              </CartProvider>
            </PermissionsProvider>
          </AuthProvider>
        </ErrorBoundaryProvider>
      </ToastProvider>
      {ReactQueryDevtoolsLazy ? (
        <React.Suspense fallback={null}>
          {React.createElement(ReactQueryDevtoolsLazy as any, { initialIsOpen: false })}
        </React.Suspense>
      ) : null}
    </QueryClientProvider>
  );
}