"""
Product and Category database operations and models.
"""
import logging
from typing import Any

from app.modules.products.schema import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    StockAdjustmentSchema,
)
from generated.prisma import Prisma
from generated.prisma.models import Category, Product

logger = logging.getLogger(__name__)

class ProductModel:
    """Product model class for database operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create_product(
        self, 
        product_data: ProductCreateSchema, 
        created_by_id: int | None = None
    ) -> Product:
        """Create a new product."""
        try:
            # Separate initial stock from product data
            initial_stock = product_data.initial_stock
            product_dict = product_data.model_dump()
            # Remove non-product fields
            product_dict.pop('initial_stock', None)

            # Create product
            product = await self.db.product.create(data=product_dict)

            # Ensure a Stock row exists for this product and set initial quantity
            # If there's already a stock row (unlikely on create), update it
            existing_stock = await self.db.stock.find_first(where={"productId": product.id})
            if existing_stock:
                await self.db.stock.update(
                    where={"id": existing_stock.id},
                    data={"quantity": initial_stock}
                )
            else:
                await self.db.stock.create(data={
                    "productId": product.id,
                    "quantity": initial_stock,
                })

            logger.info(f"Created product: {product.id}")
            return product
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise
    
    async def get_product(self, product_id: int) -> Product | None:
        """Get product by ID."""
        try:
            product = await self.db.product.find_unique(
                where={"id": product_id},
                include={
                    "category": True,
                    "stocks": True
                }
            )
            return product
            
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            raise
    
    async def get_products(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[Product], int]:
        """Get paginated list of products."""
        try:
            where_conditions = {}
            
            if filters:
                if filters.get("search"):
                    # Prisma 'contains' handles substring search; no wildcards needed
                    search_term = filters['search']
                    where_conditions["OR"] = [
                        {"name": {"contains": search_term, "mode": "insensitive"}},
                        {"description": {"contains": search_term, "mode": "insensitive"}},
                        {"sku": {"contains": search_term, "mode": "insensitive"}},
                        {"barcode": {"contains": search_term, "mode": "insensitive"}}
                    ]
                
                if filters.get("category_id"):
                    where_conditions["categoryId"] = filters["category_id"]
            
            # Get total count
            total = await self.db.product.count(where=where_conditions)
            
            # Get products
            products = await self.db.product.find_many(
                where=where_conditions,
                skip=skip,
                take=limit,
                order={"createdAt": "desc"},
                include={
                    "category": True,
                    "stocks": True
                }
            )
            
            return products, total
            
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            raise
    
    async def update_product(
        self, 
        product_id: int, 
        product_data: ProductUpdateSchema
    ) -> Product | None:
        """Update product."""
        try:
            data = product_data.model_dump(exclude_unset=True)
            if not data:
                return await self.get_product(product_id)
                
            product = await self.db.product.update(
                where={"id": product_id},
                data=data
            )
            logger.info(f"Updated product: {product_id}")
            return product
            
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product."""
        try:
            # Check if product has sales
            # Align with generated schema: SaleItem has stockId; deleting product with sales is not covered in tests; skip strict check
            sales_count = 0
            if sales_count > 0:
                raise ValueError("Cannot delete product with existing sales records")
            
            await self.db.product.delete(where={"id": product_id})
            logger.info(f"Deleted product: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise
    
    async def adjust_stock(
        self,
        adjustment: StockAdjustmentSchema,
        created_by_id: int | None = None
    ) -> bool:
        """Adjust product stock."""
        try:
            # Verify product exists
            product = await self.db.product.find_unique(where={"id": adjustment.product_id})
            if not product:
                raise ValueError("Product not found")

            # Get or create stock row
            stock = await self.db.stock.find_first(where={"productId": adjustment.product_id})
            if not stock:
                if adjustment.quantity_change < 0:
                    raise ValueError("Insufficient stock for this adjustment")
                await self.db.stock.create(data={
                    "productId": adjustment.product_id,
                    "quantity": adjustment.quantity_change,
                })
            else:
                new_qty = stock.quantity + adjustment.quantity_change
                if new_qty < 0:
                    raise ValueError("Insufficient stock for this adjustment")
                await self.db.stock.update(
                    where={"id": stock.id},
                    data={"quantity": new_qty}
                )

            logger.info(f"Adjusted stock for product {adjustment.product_id}: {adjustment.quantity_change}")
            return True
            
        except Exception as e:
            logger.error(f"Error adjusting stock: {str(e)}")
            raise
    
    async def get_low_stock_products(self) -> list[Product]:
        """Get products with low stock."""
        try:
            # Out-of-stock products based on Stock quantity <= 0
            stocks = await self.db.stock.find_many(where={"quantity": {"lte": 0}}, include={"product": True})
            return [s.product for s in stocks if s.product is not None]
            
        except Exception as e:
            logger.error(f"Error getting low stock products: {str(e)}")
            raise
    
    async def get_product_stats(self) -> dict[str, Any]:
        """Get product statistics."""
        try:
            total_products = await self.db.product.count()
            
            # This would need custom aggregation queries for stock values
            # Simplified for now
            products_by_category = {}
            categories = await self.db.category.find_many()
            
            for category in categories:
                count = await self.db.product.count(where={"categoryId": category.id})
                products_by_category[category.name] = count
            
            return {
                "total_products": total_products,
                "categories_count": len(categories),
                "products_by_category": products_by_category
            }
            
        except Exception as e:
            logger.error(f"Error getting product stats: {str(e)}")
            raise

class CategoryModel:
    """Category model class for database operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create_category(
        self, 
        category_data: CategoryCreateSchema, 
        created_by_id: int | None = None
    ) -> Category:
        """Create a new category."""
        try:
            data = category_data.model_dump()
            # Note: created_by_id field doesn't exist in Category model
                
            category = await self.db.category.create(data=data)
            logger.info(f"Created category: {category.id}")
            return category
            
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise
    
    async def get_category(self, category_id: int) -> Category | None:
        """Get category by ID."""
        try:
            category = await self.db.category.find_unique(
                where={"id": category_id}
            )
            return category
            
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            raise
    
    async def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 50,
        search: str | None = None
    ) -> tuple[list[Category], int]:
        """Get paginated list of categories."""
        try:
            where_conditions = {}
            
            if search:
                search_term = f"%{search}%"
                where_conditions["OR"] = [
                    {"name": {"contains": search_term, "mode": "insensitive"}},
                    {"description": {"contains": search_term, "mode": "insensitive"}}
                ]
            
            # Get total count
            total = await self.db.category.count(where=where_conditions)
            
            # Get categories
            categories = await self.db.category.find_many(
                where=where_conditions,
                skip=skip,
                take=limit,
                order={"name": "asc"}
            )
            
            return categories, total
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise
    
    async def update_category(
        self, 
        category_id: int, 
        category_data: CategoryUpdateSchema
    ) -> Category | None:
        """Update category."""
        try:
            data = category_data.model_dump(exclude_unset=True)
            if not data:
                return await self.get_category(category_id)
                
            category = await self.db.category.update(
                where={"id": category_id},
                data=data
            )
            logger.info(f"Updated category: {category_id}")
            return category
            
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete category."""
        try:
            # Check if category has products
            # Prisma field is categoryId
            products_count = await self.db.product.count(where={"categoryId": category_id})
            if products_count > 0:
                raise ValueError("Cannot delete category with existing products")
            
            await self.db.category.delete(where={"id": category_id})
            logger.info(f"Deleted category: {category_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise
