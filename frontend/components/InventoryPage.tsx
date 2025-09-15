import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { 
  Package, 
  Plus, 
  AlertTriangle, 
  DollarSign,
  BarChart3,
  FileX,
  RefreshCw,
  Download,
  Eye,
  Edit
} from 'lucide-react';
import { Permission } from '../context/PermissionsContext';
import { queryKeys } from '../lib/queryKeys';
import { SkeletonTable } from './SkeletonTable';
import { ErrorState } from './ErrorState';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { Input } from './ui/input';
import { useToast } from '../context/ToastContext';
import { mapError } from '../lib/errorMap';
import {
  useInventoryItems,
  useInventoryDead,
  useInventoryMovements,
  useInventorySummary,
  useInventoryValuation,
  useAdjustInventoryStock,
  useUpdateInventoryStockSettings
} from '../hooks/useInventoryQueries';
import { Require } from './Require';
import { AdjustStockModal } from './AdjustStockModal';
import { UpdateStockSettingsModal } from './UpdateStockSettingsModal';

const inventoryOverviewPlaceholder = {
  totalProducts: 0,
  totalValueCost: 0,
  totalValueRetail: 0,
  lowStock: 0,
  deadStock: 0,
  turnoverRate: 0
};

interface LowStockItem {
  id: number;
  name: string;
  sku: string;
  current: number;
  minimum: number;
  category: string;
  lastOrder: string;
}

// Removed static mock arrays; list queries below supply data

type Severity = 'high' | 'medium' | 'low' | 'unknown';

interface DeadStockItem {
  id: number;
  name: string;
  sku: string;
  quantity: number;
  daysStagnant: number;
  value: number;
  severity: Severity;
}

// Removed static dead stock mock

type MovementType = 'sale' | 'purchase' | 'adjustment' | 'other';

interface RecentMovement {
  id: number;
  product: string;
  type: MovementType;
  quantity: number; // negative for outflow, positive for inflow
  date: string;
  reference: string;
}

// Removed static movements mock

export function InventoryPage() {
  const { push } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 300);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [deadPage, setDeadPage] = useState(1);
  const [movementsPage, setMovementsPage] = useState(1);
  const [adjustModalProduct, setAdjustModalProduct] = useState<any | null>(null);
  const [thresholdModalProduct, setThresholdModalProduct] = useState<any | null>(null);

  const itemsQuery = useInventoryItems({ page, size, search: debouncedSearch || undefined, status: 'all' });
  const deadQuery = useInventoryDead({ page: deadPage, size, search: debouncedSearch || undefined });
  const movementsQuery = useInventoryMovements({ page: movementsPage, size: 25 });
  const summaryQuery = useInventorySummary();
  const valuationQuery = useInventoryValuation();

  const adjustMutation = useAdjustInventoryStock();
  const updateSettingsMutation = useUpdateInventoryStockSettings();

  const overview = React.useMemo(() => {
    const summary = summaryQuery.data as any;
    const valuation = valuationQuery.data as any;
    if (!summary && !valuation) return inventoryOverviewPlaceholder;
    const totalCost = valuation?.total_inventory_cost ?? summary?.total_inventory_cost ?? 0;
    const totalRetail = valuation?.total_inventory_retail ?? summary?.total_inventory_retail ?? 0;
    return {
      totalProducts: summary?.total_products ?? 0,
      totalValueCost: totalCost,
      totalValueRetail: totalRetail,
      lowStock: summary?.low_stock_count ?? 0,
      deadStock: summary?.dead_stock_cached ?? 0,
      turnoverRate: 0
    };
  }, [summaryQuery.data, valuationQuery.data]);

  const marginPercent = React.useMemo(() => {
    if (!overview.totalValueRetail || overview.totalValueRetail <= 0) return 0;
    const profit = overview.totalValueRetail - overview.totalValueCost;
    return profit <= 0 ? 0 : (profit / overview.totalValueRetail) * 100;
  }, [overview.totalValueRetail, overview.totalValueCost]);

  const lowStockPercent = React.useMemo(() => overview.totalProducts > 0 ? (overview.lowStock / overview.totalProducts) * 100 : 0, [overview.lowStock, overview.totalProducts]);
  const deadStockPercent = React.useMemo(() => overview.totalProducts > 0 ? (overview.deadStock / overview.totalProducts) * 100 : 0, [overview.deadStock, overview.totalProducts]);
  const inStockPercent = React.useMemo(() => {
    const val = 100 - lowStockPercent - deadStockPercent;
    return Math.max(0, Math.min(100, val));
  }, [lowStockPercent, deadStockPercent]);

  const items = (itemsQuery.data as any)?.items || [];
  const itemsPagination = (itemsQuery.data as any)?.meta?.pagination || {};
  const total = itemsPagination?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / size));

  const deadItems = (deadQuery.data as any)?.items || [];
  const deadPagination = (deadQuery.data as any)?.meta?.pagination || {};
  const deadTotal = deadPagination?.total || 0;
  const deadTotalPages = Math.max(1, Math.ceil(deadTotal / size));

  const movementItems = (movementsQuery.data as any)?.items || [];
  const movementPagination = (movementsQuery.data as any)?.meta?.pagination || {};
  const movementTotal = movementPagination?.total || 0;
  const movementTotalPages = Math.max(1, Math.ceil(movementTotal / 25));

  const getSeverityColor = (severity: Severity): string => {
    switch (severity) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getMovementTypeColor = (type: MovementType): string => {
    switch (type) {
      case 'sale': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'purchase': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'adjustment': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Inventory Management</h1>
          <p className="text-white/70">Monitor and manage your inventory across all locations</p>
        </div>
        <div className="flex space-x-2">
          <Permission perm="products:write" fallback={null}>
            <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
              <Plus className="w-4 h-4 mr-2" />
              Add Product
            </Button>
          </Permission>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20 flex flex-wrap">
          {['overview','low-stock','dead-stock','valuation','movements'].map(t => (
            <TabsTrigger key={t} value={t} className="data-[state=active]:bg-white/20 text-white">
              {t === 'overview' && 'Overview'}
              {t === 'low-stock' && 'Low Stock'}
              {t === 'dead-stock' && 'Dead Stock'}
              {t === 'valuation' && 'Valuation'}
              {t === 'movements' && 'Movements'}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Package className="w-8 h-8 text-blue-400" />
                  <div>
                    <p className="text-white/70 text-sm">Total Products</p>
                    <p className="text-white text-xl">{overview.totalProducts.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-white/70 text-sm">Inventory Cost</p>
                    <p className="text-white text-xl">${overview.totalValueCost.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-8 h-8 text-emerald-400" />
                  <div>
                    <p className="text-white/70 text-sm">Retail Value</p>
                    <p className="text-white text-xl">${overview.totalValueRetail.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-8 h-8 text-yellow-400" />
                  <div>
                    <p className="text-white/70 text-sm">Low Stock</p>
                    <p className="text-white text-xl">{overview.lowStock}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <FileX className="w-8 h-8 text-red-400" />
                  <div>
                    <p className="text-white/70 text-sm">Dead Stock</p>
                    <p className="text-white text-xl">{overview.deadStock}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-white/70 text-sm">Profit Margin</p>
                    <p className="text-white text-xl">{marginPercent.toFixed(1)}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Inventory Health</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white/70">In Stock (est)</span>
                    <span className="text-white">{inStockPercent.toFixed(1)}%</span>
                  </div>
                  <Progress value={inStockPercent} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white/70">Low Stock</span>
                    <span className="text-white">{lowStockPercent.toFixed(1)}%</span>
                  </div>
                  <Progress value={lowStockPercent} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white/70">Dead Stock</span>
                    <span className="text-white">{deadStockPercent.toFixed(1)}%</span>
                  </div>
                  <Progress value={deadStockPercent} className="h-2" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Category Distribution</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-white/70">Electronics</span>
                    <span className="text-white">1,245 items</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Accessories</span>
                    <span className="text-white">892 items</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Software</span>
                    <span className="text-white">456 items</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Services</span>
                    <span className="text-white">123 items</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="low-stock" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-white">Low Stock Items</CardTitle>
            </CardHeader>
            <CardContent>
              {itemsQuery.isLoading ? (
                <SkeletonTable rows={10} columns={4} />
              ) : itemsQuery.isError ? (
                <ErrorState message={(itemsQuery.error as any)?.message || 'Failed to load'} />
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-white/70">Product</TableHead>
                      <TableHead className="text-white/70">SKU</TableHead>
                      <TableHead className="text-white/70">Qty</TableHead>
                      <TableHead className="text-white/70">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((it: any) => (
                      <TableRow key={it.product_id} className="hover:bg-white/5">
                        <TableCell className="text-white text-sm">{it.name || '—'}</TableCell>
                        <TableCell className="text-white/60 text-xs">{it.sku || '—'}</TableCell>
                        <TableCell className="text-white text-sm">{it.quantity}</TableCell>
                        <TableCell className="text-white/70 text-xs space-x-2">
                          <Require anyOf={['inventory:adjust','products:update']}>
                            <Button size="sm" variant="outline" className="h-7 text-white/80 border-white/30" onClick={() => setAdjustModalProduct(it)}>Adj</Button>
                          </Require>
                          <Require anyOf={['products:update']}>
                            <Button size="sm" variant="outline" className="h-7 text-white/80 border-white/30" onClick={() => setThresholdModalProduct(it)}>Thresh</Button>
                          </Require>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
              <div className="flex justify-between items-center mt-4 text-white/70 text-xs">
                <span>Page {page} / {totalPages}</span>
                <div className="space-x-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p-1))}>Prev</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={page >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p+1))}>Next</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dead-stock" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-white">Dead Stock</CardTitle>
            </CardHeader>
            <CardContent>
              {deadQuery.isLoading ? <SkeletonTable rows={10} columns={5} /> : deadQuery.isError ? <ErrorState message={(deadQuery.error as any)?.message || 'Failed to load dead stock'} /> : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-white/70">Product</TableHead>
                      <TableHead className="text-white/70">SKU</TableHead>
                      <TableHead className="text-white/70">Qty</TableHead>
                      <TableHead className="text-white/70">Dead?</TableHead>
                      <TableHead className="text-white/70">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(deadQuery.data as any)?.items?.map((it: any) => (
                      <TableRow key={it.product_id} className="hover:bg-white/5">
                        <TableCell className="text-white text-sm">{it.name || '—'}</TableCell>
                        <TableCell className="text-white/60 text-xs">{it.sku || '—'}</TableCell>
                        <TableCell className="text-white text-sm">{it.quantity}</TableCell>
                        <TableCell className="text-white/60 text-xs">{it.dead_stock ? 'Yes' : 'No'}</TableCell>
                        <TableCell className="text-white/70 text-xs space-x-2">
                          <Require anyOf={['inventory:adjust','products:update']}>
                            <Button size="sm" variant="outline" className="h-7 text-white/80 border-white/30" onClick={() => setAdjustModalProduct(it)}>Adj</Button>
                          </Require>
                          <Require anyOf={['products:update']}>
                            <Button size="sm" variant="outline" className="h-7 text-white/80 border-white/30" onClick={() => setThresholdModalProduct(it)}>Thresh</Button>
                          </Require>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
              <div className="flex justify-between items-center mt-4 text-white/70 text-xs">
                <span>Page {deadPage} / {deadTotalPages}</span>
                <div className="space-x-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={deadPage <= 1} onClick={() => setDeadPage(p => Math.max(1, p-1))}>Prev</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={deadPage >= deadTotalPages} onClick={() => setDeadPage(p => Math.min(deadTotalPages, p+1))}>Next</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="valuation" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-white">Inventory Valuation</CardTitle>
            </CardHeader>
            <CardContent>
              {valuationQuery.isLoading ? <SkeletonTable rows={3} columns={3} /> : valuationQuery.isError ? <ErrorState message={(valuationQuery.error as any)?.message || 'Failed to load valuation'} /> : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="bg-white/5 border-white/10">
                    <CardContent className="p-4">
                      <p className="text-white/70 text-xs uppercase mb-1">Total Cost</p>
                      <p className="text-white text-lg">${(valuationQuery.data as any)?.total_inventory_cost?.toLocaleString?.() || 0}</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-white/5 border-white/10">
                    <CardContent className="p-4">
                      <p className="text-white/70 text-xs uppercase mb-1">Total Retail</p>
                      <p className="text-white text-lg">${(valuationQuery.data as any)?.total_inventory_retail?.toLocaleString?.() || 0}</p>
                    </CardContent>
                  </Card>
                  {(valuationQuery.data as any)?.valuationDerived && (
                    <Card className="bg-yellow-500/10 border-yellow-500/30">
                      <CardContent className="p-4">
                        <p className="text-yellow-400 text-xs">Derived from summary (valuation endpoint fallback)</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="movements" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-white">Recent Movements</CardTitle>
            </CardHeader>
            <CardContent>
              {movementsQuery.isLoading ? <SkeletonTable rows={10} columns={4} /> : movementsQuery.isError ? <ErrorState message={(movementsQuery.error as any)?.message || 'Failed to load movements'} /> : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-white/70">Type</TableHead>
                      <TableHead className="text-white/70">Product</TableHead>
                      <TableHead className="text-white/70">Qty</TableHead>
                      <TableHead className="text-white/70">Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(movementsQuery.data as any)?.items?.map((m: any, idx: number) => (
                      <TableRow key={m.id || idx} className="hover:bg-white/5">
                        <TableCell className="text-white/60 text-xs">{m.type || '—'}</TableCell>
                        <TableCell className="text-white text-sm">{m.product_name || m.product || '—'}</TableCell>
                        <TableCell className="text-white text-sm">{m.quantity}</TableCell>
                        <TableCell className="text-white/60 text-xs">{m.date || m.created_at || '—'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
              <div className="flex justify-between items-center mt-4 text-white/70 text-xs">
                <span>Page {movementsPage} / {movementTotalPages}</span>
                <div className="space-x-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={movementsPage <= 1} onClick={() => setMovementsPage(p => Math.max(1, p-1))}>Prev</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 border-white/30 text-white/80" disabled={movementsPage >= movementTotalPages} onClick={() => setMovementsPage(p => Math.min(movementTotalPages, p+1))}>Next</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      <AdjustStockModal open={!!adjustModalProduct} onOpenChange={(o) => { if(!o) setAdjustModalProduct(null); }} product={adjustModalProduct} />
      <UpdateStockSettingsModal open={!!thresholdModalProduct} onOpenChange={(o) => { if(!o) setThresholdModalProduct(null); }} product={thresholdModalProduct} />
    </div>
  );
}