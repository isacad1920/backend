import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  BarChart3, 
  Download, 
  DollarSign,
  TrendingUp,
  Users,
  Package,
  FileText
} from 'lucide-react';

const salesReportData = [
  { month: 'Jan', sales: 45000, orders: 156, customers: 89 },
  { month: 'Feb', sales: 52000, orders: 178, customers: 95 },
  { month: 'Mar', sales: 48000, orders: 162, customers: 87 },
  { month: 'Apr', sales: 61000, orders: 201, customers: 112 },
  { month: 'May', sales: 55000, orders: 189, customers: 98 },
  { month: 'Jun', sales: 67000, orders: 223, customers: 124 },
];

const branchReportData = [
  { branch: 'Main Branch', sales: 245000, orders: 456, percentage: 45 },
  { branch: 'North Branch', sales: 180000, orders: 334, percentage: 33 },
  { branch: 'South Branch', sales: 125000, orders: 234, percentage: 23 },
  { branch: 'East Branch', sales: 95000, orders: 178, percentage: 18 },
];

const productReportData = [
  { name: 'Laptop Pro 15"', value: 85000, color: '#3b82f6' },
  { name: 'Wireless Mouse', value: 48000, color: '#10b981' },
  { name: 'Monitor 24"', value: 67000, color: '#f59e0b' },
  { name: 'USB-C Cable', value: 28000, color: '#ef4444' },
  { name: 'Others', value: 45000, color: '#8b5cf6' },
];

const arAgingData = [
  { customer: 'Tech Solutions Inc', current: 12500, days30: 0, days60: 0, days90: 2500, total: 15000 },
  { customer: 'Digital Agency', current: 8900, days30: 3200, days60: 0, days90: 0, total: 12100 },
  { customer: 'Startup Co', current: 0, days30: 5600, days60: 2100, days90: 0, total: 7700 },
  { customer: 'Corp Systems', current: 22100, days30: 0, days60: 1800, days90: 0, total: 23900 },
  { customer: 'Local Business', current: 0, days30: 0, days60: 4500, days90: 1200, total: 5700 },
];

export function ReportsPage() {
  const [reportType, setReportType] = useState('sales');
  const [dateRange, setDateRange] = useState('last-6-months');
  const [startDate, setStartDate] = useState('2024-06-01');
  const [endDate, setEndDate] = useState('2024-12-15');

  const handleExport = (format: string) => {
    // Simulate export
    setTimeout(() => {
      const link = document.createElement('a');
      link.href = '#';
      link.download = `${reportType}-report.${format}`;
      link.click();
    }, 100);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl flex items-center">
            <BarChart3 className="w-6 h-6 mr-3" />
            Reports & Analytics
          </h1>
          <p className="text-white/70">Generate comprehensive business reports and insights</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => handleExport('pdf')} variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <FileText className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button onClick={() => handleExport('csv')} className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Report Filters */}
      <Card className="bg-white/10 backdrop-blur-md border-white/20">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label className="text-white">Report Type</Label>
              <Select value={reportType} onValueChange={setReportType}>
                <SelectTrigger className="bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sales">Sales Report</SelectItem>
                  <SelectItem value="ar-aging">AR Aging</SelectItem>
                  <SelectItem value="inventory">Inventory Report</SelectItem>
                  <SelectItem value="branch">Branch Performance</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-white">Date Range</Label>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger className="bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last-week">Last Week</SelectItem>
                  <SelectItem value="last-month">Last Month</SelectItem>
                  <SelectItem value="last-3-months">Last 3 Months</SelectItem>
                  <SelectItem value="last-6-months">Last 6 Months</SelectItem>
                  <SelectItem value="last-year">Last Year</SelectItem>
                  <SelectItem value="custom">Custom Range</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-white">Start Date</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="bg-white/10 border-white/20 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label className="text-white">End Date</Label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="bg-white/10 border-white/20 text-white"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="overview" className="data-[state=active]:bg-white/20 text-white">
            Overview
          </TabsTrigger>
          <TabsTrigger value="sales" className="data-[state=active]:bg-white/20 text-white">
            Sales Analytics
          </TabsTrigger>
          <TabsTrigger value="ar-aging" className="data-[state=active]:bg-white/20 text-white">
            AR Aging
          </TabsTrigger>
          <TabsTrigger value="inventory" className="data-[state=active]:bg-white/20 text-white">
            Inventory
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-white/70 text-sm">Total Revenue</p>
                    <p className="text-white text-xl">$328,000</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-8 h-8 text-blue-400" />
                  <div>
                    <p className="text-white/70 text-sm">Growth Rate</p>
                    <p className="text-white text-xl">+12.5%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="w-8 h-8 text-purple-400" />
                  <div>
                    <p className="text-white/70 text-sm">Total Customers</p>
                    <p className="text-white text-xl">605</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Package className="w-8 h-8 text-orange-400" />
                  <div>
                    <p className="text-white/70 text-sm">Products Sold</p>
                    <p className="text-white text-xl">1,409</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Sales Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={salesReportData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="rgba(255,255,255,0.7)" />
                    <YAxis stroke="rgba(255,255,255,0.7)" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(255,255,255,0.1)', 
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        backdropFilter: 'blur(12px)'
                      }} 
                    />
                    <Line type="monotone" dataKey="sales" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Product Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={productReportData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {productReportData.map((entry, index) => (
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
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="sales" className="space-y-4">
          {/* Sales by Branch */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Sales by Branch</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Branch</TableHead>
                    <TableHead className="text-white/70">Sales</TableHead>
                    <TableHead className="text-white/70">Orders</TableHead>
                    <TableHead className="text-white/70">Performance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {branchReportData.map((branch, index) => (
                    <TableRow key={index} className="border-white/20">
                      <TableCell className="text-white">{branch.branch}</TableCell>
                      <TableCell className="text-white">${branch.sales.toLocaleString()}</TableCell>
                      <TableCell className="text-white/70">{branch.orders}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-white/20 rounded-full h-2">
                            <div 
                              className="h-2 bg-blue-400 rounded-full" 
                              style={{ width: `${branch.percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-white/70 text-sm">{branch.percentage}%</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Monthly Sales Chart */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Monthly Sales Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={salesReportData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="month" stroke="rgba(255,255,255,0.7)" />
                  <YAxis stroke="rgba(255,255,255,0.7)" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(255,255,255,0.1)', 
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      backdropFilter: 'blur(12px)'
                    }} 
                  />
                  <Bar dataKey="sales" fill="#3b82f6" />
                  <Bar dataKey="orders" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ar-aging" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Accounts Receivable Aging Report</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Customer</TableHead>
                    <TableHead className="text-white/70">Current</TableHead>
                    <TableHead className="text-white/70">1-30 Days</TableHead>
                    <TableHead className="text-white/70">31-60 Days</TableHead>
                    <TableHead className="text-white/70">60+ Days</TableHead>
                    <TableHead className="text-white/70">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {arAgingData.map((customer, index) => (
                    <TableRow key={index} className="border-white/20">
                      <TableCell className="text-white">{customer.customer}</TableCell>
                      <TableCell className="text-green-400">${customer.current.toLocaleString()}</TableCell>
                      <TableCell className="text-yellow-400">${customer.days30.toLocaleString()}</TableCell>
                      <TableCell className="text-orange-400">${customer.days60.toLocaleString()}</TableCell>
                      <TableCell className="text-red-400">${customer.days90.toLocaleString()}</TableCell>
                      <TableCell className="text-white font-medium">${customer.total.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* AR Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4 text-center">
                <p className="text-white/70 text-sm">Current (0-30)</p>
                <p className="text-green-400 text-xl">$43,500</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4 text-center">
                <p className="text-white/70 text-sm">Past Due (31-60)</p>
                <p className="text-yellow-400 text-xl">$8,800</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4 text-center">
                <p className="text-white/70 text-sm">Overdue (60+)</p>
                <p className="text-red-400 text-xl">$12,600</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardContent className="p-4 text-center">
                <p className="text-white/70 text-sm">Total A/R</p>
                <p className="text-white text-xl">$64,900</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="inventory" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Inventory Valuation Report</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <Package className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                  <p className="text-white/70 mb-2">Total Items</p>
                  <p className="text-white text-2xl">3,174</p>
                </div>
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <DollarSign className="w-12 h-12 text-green-400 mx-auto mb-4" />
                  <p className="text-white/70 mb-2">Cost Value</p>
                  <p className="text-white text-2xl">$487,650</p>
                </div>
                <div className="text-center p-6 bg-white/5 rounded-lg">
                  <TrendingUp className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                  <p className="text-white/70 mb-2">Retail Value</p>
                  <p className="text-white text-2xl">$731,475</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}