"""
Product service layer for business logic.
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.exceptions import (
    AlreadyExistsError,
    APIError,
    DatabaseError,
    InsufficientStockError,
    NotFoundError,
    ValidationError,
)
from app.modules.products.model import CategoryModel, ProductModel
from app.modules.products.schema import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    CategoryUpdateSchema,
    ProductCreateSchema,
    ProductDetailResponseSchema,
    ProductListResponseSchema,
    ProductResponseSchema,
    ProductStatsSchema,
    ProductUpdateSchema,
    StockAdjustmentSchema,
    StockStatus,
)
from generated.prisma import Prisma

logger = logging.getLogger(__name__)

class ProductService:
    """Product service class for managing product operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
        self.product_model = ProductModel(db)
        self.category_model = CategoryModel(db)
    
    def _calculate_stock_status(self, current_stock: int, minimum_stock: int = 0) -> StockStatus:
        """Calculate stock status based on current and minimum stock."""
        if current_stock <= 0:
            return StockStatus.OUT_OF_STOCK
        elif current_stock <= minimum_stock:
            return StockStatus.LOW_STOCK
        else:
            return StockStatus.IN_STOCK
    
    def _calculate_profit_margin(self, cost_price: Decimal, selling_price: Decimal) -> Decimal:
        """Calculate profit margin percentage."""
        if cost_price <= 0:
            return Decimal('0')
        return ((selling_price - cost_price) / cost_price) * 100
    
    async def create_product(
        self,
        product_data: ProductCreateSchema,
        created_by_id: int | None = None
    ) -> ProductResponseSchema:
        """Create a new product."""
        try:
            # Check if SKU already exists
            existing_product = await self.db.product.find_unique(
                where={"sku": product_data.sku}
            )
            if existing_product:
                raise AlreadyExistsError("Product with this SKU already exists", error_code="PRODUCT_ALREADY_EXISTS")
            
            # Verify category exists
            category = await self.db.category.find_unique(
                where={"id": product_data.categoryId}
            )
            if not category:
                raise NotFoundError("Category not found", error_code="CATEGORY_NOT_FOUND")
            
            product = await self.product_model.create_product(product_data, created_by_id)
            
            # Convert to response schema
            # Fetch stock quantity for the created product
            stock = await self.db.stock.find_first(where={"productId": product.id})
            current_qty = stock.quantity if stock else 0
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "barcode": product.barcode,
                "categoryId": product.categoryId,
                "costPrice": product.costPrice,
                "sellingPrice": product.sellingPrice,
                "stockStatus": self._calculate_stock_status(current_qty),
                "profitMargin": self._calculate_profit_margin(product.costPrice, product.sellingPrice),
                "createdAt": product.createdAt,
                "updatedAt": product.updatedAt,
                "categoryName": category.name if category else None,
            }
            return ProductResponseSchema(**product_dict)
            
        except APIError:
            # Bubble known API errors (AlreadyExists, NotFound, Validation, etc.)
            raise
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to create product"
            )
    
    async def get_product(self, product_id: int) -> ProductDetailResponseSchema | None:
        """Get product by ID with details."""
        try:
            product = await self.product_model.get_product(product_id)
            if not product:
                return None
            
            # Calculate additional stats
            # Would need actual sales data aggregation
            total_sales = Decimal('0')
            total_sold = 0
            last_sale_date = None
            
            # Aggregate current stock from stocks relation
            current_qty = 0
            if hasattr(product, 'stocks') and product.stocks:
                for s in product.stocks:
                    try:
                        current_qty += int(s.quantity)
                    except Exception:
                        pass
            product_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "barcode": product.barcode,
                "categoryId": product.categoryId,
                "costPrice": product.costPrice,
                "sellingPrice": product.sellingPrice,
                "stockStatus": self._calculate_stock_status(current_qty),
                "profitMargin": self._calculate_profit_margin(product.costPrice, product.sellingPrice),
                "createdAt": product.createdAt,
                "updatedAt": product.updatedAt,
                "categoryName": product.category.name if hasattr(product, 'category') and product.category else None,
                "totalSales": total_sales,
                "totalSold": total_sold,
                "lastSaleDate": last_sale_date,
                "lastStockUpdate": datetime.now(),
                "createdByName": None,
            }
            return ProductDetailResponseSchema(**product_dict)
            
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to get product"
            )
    
    async def list_products(
        self,
        page: int = 1,
        size: int = 20,
        filters: dict[str, Any] | None = None
    ) -> ProductListResponseSchema:
        """Get paginated list of products."""
        try:
            skip = (page - 1) * size
            products, total = await self.product_model.get_products(
                skip=skip, limit=size, filters=filters
            )
            
            pages = (total + size - 1) // size
            
            items: list[ProductResponseSchema] = []
            for product in products:
                # sum stock quantities if preloaded
                current_qty = 0
                if hasattr(product, 'stocks') and product.stocks:
                    for s in product.stocks:
                        try:
                            current_qty += int(s.quantity)
                        except Exception:
                            pass
                p_dict = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "sku": product.sku,
                    "barcode": product.barcode,
                    "categoryId": product.categoryId,
                    "costPrice": product.costPrice,
                    "sellingPrice": product.sellingPrice,
                    "stockStatus": self._calculate_stock_status(current_qty),
                    "profitMargin": self._calculate_profit_margin(product.costPrice, product.sellingPrice),
                    "createdAt": product.createdAt,
                    "updatedAt": product.updatedAt,
                    "categoryName": product.category.name if hasattr(product, 'category') and product.category else None,
                }
                items.append(ProductResponseSchema(**p_dict))

            return ProductListResponseSchema(
                items=items,
                total=total,
                page=page,
                size=size,
            )
            
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to list products"
            )
    
    async def update_product(
        self,
        product_id: int,
        product_data: ProductUpdateSchema
    ) -> ProductResponseSchema:
        """Update product."""
        try:
            # Check if product exists
            existing_product = await self.product_model.get_product(product_id)
            if not existing_product:
                raise NotFoundError("Product not found", error_code="PRODUCT_NOT_FOUND")
            
            # Check for SKU conflicts if SKU is being updated
            if product_data.sku and product_data.sku != existing_product.sku:
                sku_conflict = await self.db.product.find_first(
                    where={
                        "sku": product_data.sku,
                        "id": {"not": product_id}
                    }
                )
                if sku_conflict:
                    raise AlreadyExistsError("Product with this SKU already exists", error_code="PRODUCT_ALREADY_EXISTS")
            
            # Verify category if being updated
            if product_data.categoryId:
                category = await self.db.category.find_unique(
                    where={"id": product_data.categoryId}
                )
                if not category:
                    raise NotFoundError("Category not found", error_code="CATEGORY_NOT_FOUND")
            
            product = await self.product_model.update_product(product_id, product_data)
            
            # Get current stock
            stock = await self.db.stock.find_first(where={"productId": product.id})
            current_qty = stock.quantity if stock else 0
            p_dict = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "sku": product.sku,
                "barcode": product.barcode,
                "categoryId": product.categoryId,
                "costPrice": product.costPrice,
                "sellingPrice": product.sellingPrice,
                "stockStatus": self._calculate_stock_status(current_qty),
                "profitMargin": self._calculate_profit_margin(product.costPrice, product.sellingPrice),
                "createdAt": product.createdAt,
                "updatedAt": product.updatedAt,
                "categoryName": product.category.name if hasattr(product, 'category') and product.category else None,
            }
            return ProductResponseSchema(**p_dict)
            
        except (NotFoundError, AlreadyExistsError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to update product"
            )
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product."""
        try:
            # Check if product exists
            existing_product = await self.product_model.get_product(product_id)
            if not existing_product:
                raise NotFoundError("Product not found", error_code="PRODUCT_NOT_FOUND")
            
            success = await self.product_model.delete_product(product_id)
            return success
            
        except NotFoundError:
            raise
        except Exception as e:
            if "Cannot delete product" in str(e):
                raise DatabaseError(
                    error_code="VALIDATION_ERROR",
                    detail=str(e)
                )
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to delete product"
            )
    
    async def adjust_stock(
        self,
        adjustment: StockAdjustmentSchema,
        created_by_id: int | None = None
    ) -> bool:
        """Adjust product stock."""
        try:
            success = await self.product_model.adjust_stock(adjustment, created_by_id)
            return success
            
        except Exception as e:
            if "Product not found" in str(e):
                raise NotFoundError("Product not found", error_code="PRODUCT_NOT_FOUND")
            if "Insufficient stock" in str(e):
                raise InsufficientStockError("Insufficient stock")
            logger.error(f"Error adjusting stock: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to adjust stock"
            )
    
    async def get_product_statistics(self) -> ProductStatsSchema:
        """Get product statistics."""
        try:
            stats = await self.product_model.get_product_stats()
            # Normalize keys to match ProductStatsSchema (camelCase)
            normalized = {
                "totalProducts": stats.get("total_products") or stats.get("totalProducts") or 0,
                "categoriesCount": stats.get("categories_count") or stats.get("categoriesCount") or 0,
                "productsByCategory": stats.get("products_by_category") or stats.get("productsByCategory") or {},
            }
            return ProductStatsSchema(**normalized)
            
        except Exception as e:
            logger.error(f"Error getting product statistics: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to get product statistics"
            )

class CategoryService:
    """Category service class for managing category operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
        self.category_model = CategoryModel(db)
        self.product_model = ProductModel(db)
    
    async def create_category(
        self,
        category_data: CategoryCreateSchema,
        created_by_id: int | None = None
    ) -> CategoryResponseSchema:
        """Create a new category."""
        try:
            # Check if category name already exists
            existing_category = await self.db.category.find_first(
                where={"name": category_data.name}
            )
            if existing_category:
                raise AlreadyExistsError("Category with this name already exists", error_code="CATEGORY_ALREADY_EXISTS")
            
            category = await self.category_model.create_category(category_data, created_by_id)
            
            category_dict = category.model_dump() if hasattr(category, 'model_dump') else category.__dict__
            category_dict["product_count"] = 0
            
            return CategoryResponseSchema(**category_dict)
            
        except (AlreadyExistsError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to create category"
            )
    
    async def get_category(self, category_id: int) -> CategoryResponseSchema | None:
        """Get category by ID."""
        try:
            category = await self.category_model.get_category(category_id)
            if not category:
                return None
            
            category_dict = category.model_dump() if hasattr(category, 'model_dump') else category.__dict__
            # Compute product_count explicitly
            product_count = await self.product_model.db.product.count(where={"categoryId": category.id})
            category_dict["product_count"] = product_count
            
            return CategoryResponseSchema(**category_dict)
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to get category"
            )
    
    async def list_categories(
        self,
        page: int = 1,
        size: int = 50,
        search: str | None = None
    ) -> list[CategoryResponseSchema]:
        """Get list of categories."""
        try:
            skip = (page - 1) * size
            categories, total = await self.category_model.get_categories(
                skip=skip, limit=size, search=search
            )
            
            category_responses = []
            for category in categories:
                category_dict = category.model_dump() if hasattr(category, 'model_dump') else category.__dict__
                # Get product count separately
                product_count = await self.product_model.db.product.count(where={"categoryId": category.id})
                category_dict["product_count"] = product_count
                category_responses.append(CategoryResponseSchema(**category_dict))
            
            return category_responses
        except Exception as e:
            logger.error(f"Error listing categories: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to list categories"
            )
    
    async def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdateSchema
    ) -> CategoryResponseSchema:
        """Update category."""
        try:
            # Check if category exists
            existing_category = await self.category_model.get_category(category_id)
            if not existing_category:
                raise NotFoundError("Category not found", error_code="CATEGORY_NOT_FOUND")
            
            # Check for name conflicts if name is being updated
            if category_data.name and category_data.name != existing_category.name:
                name_conflict = await self.db.category.find_first(
                    where={
                        "name": category_data.name,
                        "id": {"not": category_id}
                    }
                )
                if name_conflict:
                    raise AlreadyExistsError("Category with this name already exists", error_code="CATEGORY_ALREADY_EXISTS")
            
            category = await self.category_model.update_category(category_id, category_data)
            
            category_dict = category.model_dump() if hasattr(category, 'model_dump') else category.__dict__
            product_count = await self.product_model.db.product.count(where={"categoryId": category.id})
            category_dict["product_count"] = product_count
            
            return CategoryResponseSchema(**category_dict)
            
        except (NotFoundError, AlreadyExistsError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to update category"
            )
    
    async def delete_category(self, category_id: int) -> bool:
        """Delete category."""
        try:
            # Check if category exists
            existing_category = await self.category_model.get_category(category_id)
            if not existing_category:
                raise NotFoundError("Category not found", error_code="CATEGORY_NOT_FOUND")
            
            success = await self.category_model.delete_category(category_id)
            return success
            
        except NotFoundError:
            raise
        except Exception as e:
            if "Cannot delete category" in str(e):
                raise DatabaseError(
                    error_code="VALIDATION_ERROR",
                    detail=str(e)
                )
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise DatabaseError(
                error_code="PRODUCT_DATABASE_ERROR",
                detail="Failed to delete category"
            )

# Service factory functions
def create_product_service(db: Prisma) -> ProductService:
    """Create product service instance."""
    return ProductService(db)

def create_category_service(db: Prisma) -> CategoryService:
    """Create category service instance."""
    return CategoryService(db)
