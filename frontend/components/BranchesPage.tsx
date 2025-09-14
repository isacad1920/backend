import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { 
  Plus, 
  Search, 
  Building2, 
  Users,
  MapPin,
  Phone,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

const branchesData = [
  { 
    id: 1, 
    name: 'Main Branch', 
    address: '123 Business Ave, Downtown',
    phone: '+1 (555) 123-4567',
    manager: 'John Smith',
    employees: 12,
    revenue: 245000,
    status: 'active'
  },
  { 
    id: 2, 
    name: 'North Branch', 
    address: '456 North St, Uptown',
    phone: '+1 (555) 234-5678',
    manager: 'Sarah Johnson',
    employees: 8,
    revenue: 180000,
    status: 'active'
  },
  { 
    id: 3, 
    name: 'South Branch', 
    address: '789 South Blvd, Southside',
    phone: '+1 (555) 345-6789',
    manager: 'Mike Wilson',
    employees: 6,
    revenue: 125000,
    status: 'active'
  },
  { 
    id: 4, 
    name: 'East Branch', 
    address: '321 East End Rd, Eastside',
    phone: '+1 (555) 456-7890',
    manager: 'Lisa Chen',
    employees: 5,
    revenue: 95000,
    status: 'inactive'
  },
];

export function BranchesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBranch, setSelectedBranch] = useState(branchesData[0]);

  const filteredBranches = branchesData.filter(branch =>
    branch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    branch.manager.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    return status === 'active' 
      ? 'bg-green-500/20 text-green-400 border-green-500/30'
      : 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Branch Management</h1>
          <p className="text-white/70">Manage your business locations and operations</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            Add Branch
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Branch List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input
                  placeholder="Search branches..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
            </CardContent>
          </Card>

          {/* Branch Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Branches</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Branch</TableHead>
                    <TableHead className="text-white/70">Manager</TableHead>
                    <TableHead className="text-white/70">Employees</TableHead>
                    <TableHead className="text-white/70">Revenue</TableHead>
                    <TableHead className="text-white/70">Status</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredBranches.map((branch) => (
                    <TableRow 
                      key={branch.id} 
                      className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedBranch?.id === branch.id ? 'bg-white/10' : ''}`}
                      onClick={() => setSelectedBranch(branch)}
                    >
                      <TableCell>
                        <div>
                          <p className="text-white">{branch.name}</p>
                          <p className="text-white/70 text-sm">{branch.address}</p>
                        </div>
                      </TableCell>
                      <TableCell className="text-white">{branch.manager}</TableCell>
                      <TableCell className="text-white/70">{branch.employees}</TableCell>
                      <TableCell className="text-white">${branch.revenue.toLocaleString()}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(branch.status)}>
                          {branch.status}
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
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>

        {/* Branch Details */}
        <div className="space-y-4">
          {selectedBranch && (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Branch Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="text-white text-lg">{selectedBranch.name}</h3>
                    <Badge className={getStatusColor(selectedBranch.status)}>
                      {selectedBranch.status}
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-white/50 mt-1" />
                      <span className="text-white/70 text-sm">{selectedBranch.address}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Phone className="w-4 h-4 text-white/50" />
                      <span className="text-white/70 text-sm">{selectedBranch.phone}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Users className="w-4 h-4 text-white/50" />
                      <span className="text-white/70 text-sm">Manager: {selectedBranch.manager}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Performance</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Users className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Employees</p>
                      <p className="text-white text-lg">{selectedBranch.employees}</p>
                    </div>
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Building2 className="w-6 h-6 text-green-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Monthly Revenue</p>
                      <p className="text-white text-lg">${selectedBranch.revenue.toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                    <Users className="w-4 h-4 mr-2" />
                    Manage Staff
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    View Inventory
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    Sales Report
                  </Button>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}