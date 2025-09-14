import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { 
  Plus, 
  Search, 
  Tag, 
  Package,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';

const categoriesData = [
  { 
    id: 1, 
    name: 'Electronics', 
    description: 'Electronic devices and components',
    productCount: 245,
    totalValue: 185000,
    parentId: null
  },
  { 
    id: 2, 
    name: 'Laptops', 
    description: 'Portable computers and accessories',
    productCount: 45,
    totalValue: 85000,
    parentId: 1
  },
  { 
    id: 3, 
    name: 'Accessories', 
    description: 'Computer and electronic accessories',
    productCount: 156,
    totalValue: 25000,
    parentId: null
  },
  { 
    id: 4, 
    name: 'Cables', 
    description: 'Various types of cables and connectors',
    productCount: 89,
    totalValue: 8900,
    parentId: 3
  },
  { 
    id: 5, 
    name: 'Software', 
    description: 'Software licenses and digital products',
    productCount: 78,
    totalValue: 45000,
    parentId: null
  },
  { 
    id: 6, 
    name: 'Monitors', 
    description: 'Computer monitors and displays',
    productCount: 34,
    totalValue: 28000,
    parentId: 1
  },
];

export function CategoriesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(categoriesData[0]);

  const filteredCategories = categoriesData.filter(category =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getParentName = (parentId: number | null | undefined) => {
    if (!parentId) return 'Root Category';
    const parent = categoriesData.find(cat => cat.id === parentId);
    return parent ? parent.name : 'Unknown';
  };

  const getChildCategories = (parentId: number) => {
    return categoriesData.filter(cat => cat.parentId === parentId);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Category Management</h1>
          <p className="text-white/70">Organize your products into categories</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            Add Category
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                <Input
                  placeholder="Search categories..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                />
              </div>
            </CardContent>
          </Card>

          {/* Category Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Category</TableHead>
                    <TableHead className="text-white/70">Parent</TableHead>
                    <TableHead className="text-white/70">Products</TableHead>
                    <TableHead className="text-white/70">Total Value</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCategories.map((category) => (
                    <TableRow 
                      key={category.id} 
                      className={`border-white/20 cursor-pointer hover:bg-white/5 ${selectedCategory?.id === category.id ? 'bg-white/10' : ''}`}
                      onClick={() => setSelectedCategory(category)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Tag className="w-4 h-4 text-blue-400" />
                          <div>
                            <p className="text-white">{category.name}</p>
                            <p className="text-white/70 text-sm">{category.description}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-white/70">{getParentName(category.parentId)}</TableCell>
                      <TableCell className="text-white">{category.productCount}</TableCell>
                      <TableCell className="text-white">${category.totalValue.toLocaleString()}</TableCell>
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

        {/* Category Details */}
        <div className="space-y-4">
          {selectedCategory && (
            <>
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Category Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Tag className="w-6 h-6 text-blue-400" />
                    <div>
                      <h3 className="text-white">{selectedCategory.name}</h3>
                      <p className="text-white/70 text-sm">{selectedCategory.description}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Parent Category</span>
                      <span className="text-white text-sm">{getParentName(selectedCategory.parentId)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Product Count</span>
                      <span className="text-white text-sm">{selectedCategory.productCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/70 text-sm">Total Value</span>
                      <span className="text-white text-sm">${selectedCategory.totalValue.toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Package className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Products</p>
                      <p className="text-white text-lg">{selectedCategory.productCount}</p>
                    </div>
                    <div className="text-center p-3 bg-white/5 rounded-lg">
                      <Tag className="w-6 h-6 text-green-400 mx-auto mb-1" />
                      <p className="text-white/70 text-xs">Subcategories</p>
                      <p className="text-white text-lg">{getChildCategories(selectedCategory.id).length}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {getChildCategories(selectedCategory.id).length > 0 && (
                <Card className="bg-white/10 backdrop-blur-md border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Subcategories</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {getChildCategories(selectedCategory.id).map((child) => (
                        <div key={child.id} className="flex items-center justify-between p-2 bg-white/5 rounded">
                          <div className="flex items-center space-x-2">
                            <Tag className="w-3 h-3 text-blue-400" />
                            <span className="text-white text-sm">{child.name}</span>
                          </div>
                          <span className="text-white/70 text-xs">{child.productCount} items</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Subcategory
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    <Package className="w-4 h-4 mr-2" />
                    View Products
                  </Button>
                  <Button variant="outline" className="w-full border-white/30 text-white hover:bg-white/10">
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Category
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