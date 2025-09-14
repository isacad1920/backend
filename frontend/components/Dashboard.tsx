import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Users, Package, AlertTriangle, Plus, ArrowUpRight } from 'lucide-react';
import { dashboardService } from '../services/dashboard';
import { healthService } from '../services/health';
import type { DashboardStats } from '../types';
import { toast } from 'sonner';

// TODO: Replace placeholders with real analytics once backend endpoints standardized
interface SalesChartPoint { date: string; sales: number; revenue: number; }
interface TopProductItem { product: { id: number; name: string; sku: string; }; totalSold: number; revenue: number; }
interface LowStockAlert { product: { id: number; name: string; sku: string; }; currentStock: number; minimumStock: number; stockStatus: 'low' | 'out'; }

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  // Removed unused local summary states (todaySummary, inventorySummary) to satisfy lint; stats holds aggregated values
  const [salesChart, setSalesChart] = useState<SalesChartPoint[]>([]);
  const [topProducts, setTopProducts] = useState<TopProductItem[]>([]);
  const [lowStockAlerts, setLowStockAlerts] = useState<LowStockAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // First test backend connection
        const isConnected = await healthService.testConnection();
        setBackendConnected(isConnected);

        if (!isConnected) {
          // If backend is not connected, show offline message and use mock data
          toast.warning('Backend not connected. Using offline mode.');
        }

    // Load real aggregated stats (today + inventory)
    const aggregated = await dashboardService.getAggregatedStats({ includeLowStock: true });

        // Optional: placeholder legacy stats mapping until component refactor
        setStats({
          totalSales: aggregated.today.total_revenue,
          totalRevenue: aggregated.today.total_revenue,
          totalCustomers: 0, // backend endpoint pending
          totalProducts: aggregated.inventory.total_products,
          salesGrowth: 0,
          revenueGrowth: 0,
          customerGrowth: 0,
          productGrowth: 0
        });
        // Temporary placeholders for charts & lists until analytics endpoints wired
  setSalesChart(aggregated.today.top_selling_products.map((p: any, idx: number) => ({
          date: aggregated.today.date,
          sales: p.total_quantity,
          revenue: parseFloat(aggregated.today.total_revenue || '0') / (idx + 1)
        })));
        setTopProducts(aggregated.today.top_selling_products.map((p: any) => ({
          product: { id: p.product_id, name: p.product_name, sku: p.product_sku },
          totalSold: p.total_quantity,
          revenue: parseFloat(aggregated.today.total_revenue || '0')
        })));
        // Low stock count only (no detailed endpoint yet for alerts in new unified service here)
        if (aggregated.lowStock && aggregated.lowStock.length) {
          setLowStockAlerts(aggregated.lowStock.slice(0, 10).map(i => ({
            product: { id: i.product_id || 0, name: i.name || 'Unknown', sku: i.sku || 'N/A' },
            currentStock: i.quantity,
            minimumStock: i.min_stock ?? 0,
            stockStatus: i.quantity === 0 ? 'out' : 'low'
          })));
        } else {
          setLowStockAlerts([]);
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
        
        if (err instanceof Error && err.message.includes('timeout')) {
          toast.error('Connection timeout. Please check your network connection.');
        } else {
          toast.error('Failed to load dashboard data');
        }
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  // Default data for charts while loading
  const inventoryData = [
    { name: 'In Stock', value: 2840, color: '#10b981' },
    { name: 'Low Stock', value: 245, color: '#f59e0b' },
    { name: 'Out of Stock', value: 89, color: '#ef4444' },
  ];

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48 mb-2 bg-white/20" />
            <Skeleton className="h-4 w-96 bg-white/10" />
          </div>
          <div className="flex space-x-2">
            <Skeleton className="h-10 w-32 bg-white/20" />
            <Skeleton className="h-10 w-32 bg-white/20" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <Skeleton className="h-4 w-24 bg-white/20" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32 mb-2 bg-white/20" />
                <Skeleton className="h-4 w-36 bg-white/10" />
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <Card key={i} className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <Skeleton className="h-6 w-48 bg-white/20" />
                <Skeleton className="h-4 w-64 bg-white/10" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[300px] w-full bg-white/10" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/10 backdrop-blur-md border-red-500/30 rounded-lg p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-red-400 text-xl mb-2">Failed to Load Dashboard</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <Button 
            onClick={() => window.location.reload()} 
            className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-white text-2xl">Dashboard</h1>
            {backendConnected !== null && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${
                backendConnected 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  backendConnected ? 'bg-green-400' : 'bg-yellow-400'
                }`}></div>
                <span>{backendConnected ? 'Online' : 'Offline'}</span>
              </div>
            )}
          </div>
          <p className="text-white/70">Welcome back! Here&apos;s what&apos;s happening with your business.</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            Quick Sale
          </Button>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            Export Data
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm text-white/70">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-white/70" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-white">${stats?.totalRevenue || '0'}</div>
            <div className="flex items-center text-sm">
              {(stats?.revenueGrowth || 0) >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
              )}
              <span className={(stats?.revenueGrowth || 0) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {(stats?.revenueGrowth || 0) >= 0 ? '+' : ''}{(stats?.revenueGrowth || 0).toFixed(1)}%
              </span>
              <span className="text-white/70 ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm text-white/70">Total Sales</CardTitle>
            <ShoppingCart className="h-4 w-4 text-white/70" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-white">${stats?.totalSales || '0'}</div>
            <div className="flex items-center text-sm">
              {(stats?.salesGrowth || 0) >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
              )}
              <span className={(stats?.salesGrowth || 0) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {(stats?.salesGrowth || 0) >= 0 ? '+' : ''}{(stats?.salesGrowth || 0).toFixed(1)}%
              </span>
              <span className="text-white/70 ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm text-white/70">Total Products</CardTitle>
            <Package className="h-4 w-4 text-white/70" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-white">{stats?.totalProducts || 0}</div>
            <div className="flex items-center text-sm">
              {(stats?.productGrowth || 0) >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
              )}
              <span className={(stats?.productGrowth || 0) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {(stats?.productGrowth || 0) >= 0 ? '+' : ''}{(stats?.productGrowth || 0).toFixed(1)}%
              </span>
              <span className="text-white/70 ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm text-white/70">Active Customers</CardTitle>
            <Users className="h-4 w-4 text-white/70" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-white">{stats?.totalCustomers || 0}</div>
            <div className="flex items-center text-sm">
              {(stats?.customerGrowth || 0) >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
              )}
              <span className={(stats?.customerGrowth || 0) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {(stats?.customerGrowth || 0) >= 0 ? '+' : ''}{(stats?.customerGrowth || 0).toFixed(1)}%
              </span>
              <span className="text-white/70 ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Revenue & Profit Trends</CardTitle>
            <CardDescription className="text-white/70">
              Monthly revenue and profit over the last 6 months
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesChart.length > 0 ? salesChart : []}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255,255,255,0.1)', 
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(12px)'
                  }} 
                />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="sales" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Inventory Distribution */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Inventory Status</CardTitle>
            <CardDescription className="text-white/70">
              Current inventory distribution across all branches
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={inventoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {inventoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255,255,255,0.1)', 
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(12px)'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center space-x-4 mt-4">
              {inventoryData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-white/70 text-sm">{item.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Products */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Top Selling Products</CardTitle>
            <CardDescription className="text-white/70">
              Best performing products this month
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProducts.length > 0 ? topProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <Package className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="text-white text-sm">{product.product.name}</p>
                      <p className="text-white/70 text-xs">{product.totalSold} units sold</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <span className="text-white">${product.revenue.toLocaleString()}</span>
                      <ArrowUpRight className="w-4 h-4 text-green-400" />
                    </div>
                  </div>
                </div>
              )) : (
                <p className="text-white/70 text-center py-4">No top products data available</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Low Stock Alerts */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Low Stock Alerts</CardTitle>
            <CardDescription className="text-white/70">
              Products requiring attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {lowStockAlerts.length > 0 ? lowStockAlerts.map((alert, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    </div>
                    <div>
                      <p className="text-white text-sm">{alert.product.name}</p>
                      <p className="text-white/70 text-xs">SKU: {alert.product.sku}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-white">{alert.currentStock} / {alert.minimumStock}</p>
                    <Badge 
                      variant="secondary"
                      className={alert.stockStatus === 'out' 
                        ? 'bg-red-500/20 text-red-400 border-red-500/30' 
                        : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                      }
                    >
                      {alert.stockStatus === 'out' ? 'Out of Stock' : 'Low Stock'}
                    </Badge>
                  </div>
                </div>
              )) : (
                <p className="text-white/70 text-center py-4">No stock alerts</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Alerts */}
      {lowStockAlerts.length > 0 && (
        <Card className="bg-yellow-500/10 backdrop-blur-md border-yellow-500/30">
          <CardHeader>
            <CardTitle className="text-yellow-400 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              System Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-yellow-200">• {lowStockAlerts.length} products are running low on stock</p>
              <p className="text-yellow-200">• System is running normally</p>
              <p className="text-yellow-200">• All services are operational</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}