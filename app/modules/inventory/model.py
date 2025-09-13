"""
Inventory module data models.

This module contains the data models used by the inventory module.
"""

from generated.prisma.models import Product, Category

# Re-export models for convenience  
__all__ = [
    "Product",
    "Category"
]

# Model type aliases for better code documentation
InventoryProduct = Product
ProductCategory = Category
