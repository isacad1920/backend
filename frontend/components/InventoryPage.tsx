import React from 'react';
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

const inventoryOverview = {
  totalProducts: 3174,
  totalValue: 487650,
  lowStock: 23,
  outOfStock: 5,
  turnoverRate: 4.2
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

const lowStockItems: LowStockItem[] = [
  { id: 1, name: 'Laptop Pro 15"', sku: 'LP-001', current: 5, minimum: 10, category: 'Electronics', lastOrder: '2024-12-01' },
  { id: 2, name: 'Wireless Mouse', sku: 'WM-002', current: 8, minimum: 25, category: 'Electronics', lastOrder: '2024-11-28' },
  { id: 3, name: 'USB-C Cable', sku: 'UC-003', current: 12, minimum: 50, category: 'Accessories', lastOrder: '2024-12-05' },
  { id: 4, name: 'Monitor 24"', sku: 'M24-004', current: 3, minimum: 15, category: 'Electronics', lastOrder: '2024-11-30' },
];

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

const deadStockItems: DeadStockItem[] = [
  { id: 1, name: 'Old Laptop Model', sku: 'OL-001', quantity: 45, daysStagnant: 180, value: 22500, severity: 'high' },
  { id: 2, name: 'Legacy Cable', sku: 'LC-002', quantity: 120, daysStagnant: 120, value: 2400, severity: 'medium' },
  { id: 3, name: 'Outdated Accessory', sku: 'OA-003', quantity: 78, daysStagnant: 90, value: 1560, severity: 'low' },
];

type MovementType = 'sale' | 'purchase' | 'adjustment' | 'other';

interface RecentMovement {
  id: number;
  product: string;
  type: MovementType;
  quantity: number; // negative for outflow, positive for inflow
  date: string;
  reference: string;
}

const recentMovements: RecentMovement[] = [
  { id: 1, product: 'Laptop Pro 15"', type: 'sale', quantity: -2, date: '2024-12-15', reference: 'SAL-001' },
  { id: 2, product: 'Wireless Mouse', type: 'purchase', quantity: +50, date: '2024-12-14', reference: 'PO-045' },
  { id: 3, product: 'USB-C Cable', type: 'adjustment', quantity: -5, date: '2024-12-14', reference: 'ADJ-012' },
  { id: 4, product: 'Monitor 24"', type: 'sale', quantity: -1, date: '2024-12-13', reference: 'SAL-003' },
];

export function InventoryPage() {

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
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            Add Product
          </Button>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="overview" className="data-[state=active]:bg-white/20 text-white">
            Overview
          </TabsTrigger>
          <TabsTrigger value="low-stock" className="data-[state=active]:bg-white/20 text-white">
            Low Stock
          </TabsTrigger>
          <TabsTrigger value="dead-stock" className="data-[state=active]:bg-white/20 text-white">
            Dead Stock
          </TabsTrigger>
          <TabsTrigger value="valuation" className="data-[state=active]:bg-white/20 text-white">
            Valuation
          </TabsTrigger>
          <TabsTrigger value="movements" className="data-[state=active]:bg-white/20 text-white">
            Movements
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Package className="w-8 h-8 text-blue-400" />
                  <div>
                    <p className="text-white/70 text-sm">Total Products</p>
                    <p className="text-white text-xl">{inventoryOverview.totalProducts.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-white/70 text-sm">Total Value</p>
                    <p className="text-white text-xl">${inventoryOverview.totalValue.toLocaleString()}</p>
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
                    <p className="text-white text-xl">{inventoryOverview.lowStock}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <FileX className="w-8 h-8 text-red-400" />
                  <div>
                    <p className="text-white/70 text-sm">Out of Stock</p>
                    <p className="text-white text-xl">{inventoryOverview.outOfStock}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-white/70 text-sm">Turnover Rate</p>
                    <p className="text-white text-xl">{inventoryOverview.turnoverRate}x</p>
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
                    <span className="text-white/70">In Stock</span>
                    <span className="text-white">89%</span>
                  </div>
                  <Progress value={89} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white/70">Low Stock</span>
                    <span className="text-white">8%</span>
                  </div>
                  <Progress value={8} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-white/70">Out of Stock</span>
                    <span className="text-white">3%</span>
                  </div>
                  <Progress value={3} className="h-2" />
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
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white">Low Stock Items</CardTitle>
              <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
                <RefreshCw className="w-4 h-4 mr-2" />
                Reorder Selected
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Product</TableHead>
                    <TableHead className="text-white/70">SKU</TableHead>
                    <TableHead className="text-white/70">Current</TableHead>
                    <TableHead className="text-white/70">Minimum</TableHead>
                    <TableHead className="text-white/70">Category</TableHead>
                    <TableHead className="text-white/70">Last Order</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lowStockItems.map((item) => (
                    <TableRow key={item.id} className="border-white/20">
                      <TableCell className="text-white">{item.name}</TableCell>
                      <TableCell className="text-white/70">{item.sku}</TableCell>
                      <TableCell>
                        <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                          {item.current}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white/70">{item.minimum}</TableCell>
                      <TableCell className="text-white/70">{item.category}</TableCell>
                      <TableCell className="text-white/70">{item.lastOrder}</TableCell>
                      <TableCell>
                        <Button size="sm" className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
                          Reorder
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dead-stock" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Dead Stock Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Product</TableHead>
                    <TableHead className="text-white/70">SKU</TableHead>
                    <TableHead className="text-white/70">Quantity</TableHead>
                    <TableHead className="text-white/70">Days Stagnant</TableHead>
                    <TableHead className="text-white/70">Value</TableHead>
                    <TableHead className="text-white/70">Severity</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {deadStockItems.map((item) => (
                    <TableRow key={item.id} className="border-white/20">
                      <TableCell className="text-white">{item.name}</TableCell>
                      <TableCell className="text-white/70">{item.sku}</TableCell>
                      <TableCell className="text-white/70">{item.quantity}</TableCell>
                      <TableCell className="text-white/70">{item.daysStagnant} days</TableCell>
                      <TableCell className="text-white">${item.value.toLocaleString()}</TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(item.severity)}>
                          {item.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="valuation" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Inventory Valuation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <p className="text-white/70 text-sm mb-2">Cost Value</p>
                  <p className="text-white text-2xl">$487,650</p>
                  <p className="text-green-400 text-sm">+5.2% from last month</p>
                </div>
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <p className="text-white/70 text-sm mb-2">Retail Value</p>
                  <p className="text-white text-2xl">$731,475</p>
                  <p className="text-green-400 text-sm">+4.8% from last month</p>
                </div>
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <p className="text-white/70 text-sm mb-2">Margin</p>
                  <p className="text-white text-2xl">33.3%</p>
                  <p className="text-blue-400 text-sm">Avg profit margin</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="movements" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Recent Stock Movements</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Product</TableHead>
                    <TableHead className="text-white/70">Type</TableHead>
                    <TableHead className="text-white/70">Quantity</TableHead>
                    <TableHead className="text-white/70">Date</TableHead>
                    <TableHead className="text-white/70">Reference</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentMovements.map((movement) => (
                    <TableRow key={movement.id} className="border-white/20">
                      <TableCell className="text-white">{movement.product}</TableCell>
                      <TableCell>
                        <Badge className={getMovementTypeColor(movement.type)}>
                          {movement.type}
                        </Badge>
                      </TableCell>
                      <TableCell className={movement.quantity > 0 ? "text-green-400" : "text-red-400"}>
                        {movement.quantity > 0 ? `+${movement.quantity}` : movement.quantity}
                      </TableCell>
                      <TableCell className="text-white/70">{movement.date}</TableCell>
                      <TableCell className="text-white/70">{movement.reference}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}