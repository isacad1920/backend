"""
Branch service layer for business logic.
"""
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from generated.prisma import Prisma

from app.core.config import UserRole
from app.core.exceptions import (
    AlreadyExistsError, NotFoundError, ValidationError, 
    DatabaseError, AuthorizationError, BusinessRuleError
)
from app.modules.branches.model import BranchModel
from app.modules.branches.schema import (
    BranchCreateSchema, BranchUpdateSchema, BranchResponseSchema,
    BranchDetailResponseSchema, BranchListResponseSchema, BranchStatsSchema,
    BulkBranchUpdateSchema, BulkBranchStatusUpdateSchema, BulkOperationResponseSchema
)

logger = logging.getLogger(__name__)

class BranchService:
    """Branch service class for managing branch operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
        self.branch_model = BranchModel(db)
    
    async def create_branch(
        self,
        branch_data: BranchCreateSchema,
        created_by_id: Optional[int] = None
    ) -> BranchResponseSchema:
        """Create a new branch."""
        # Check if branch name already exists
        existing_branch = await self.db.branch.find_first(
            where={"name": branch_data.name}
        )
        if existing_branch:
            # Use message arg; attach custom code in details if needed
            raise AlreadyExistsError(
                "Branch with this name already exists",
                details={"code": "BRANCH_NAME_EXISTS"}
            )

        branch = await self.branch_model.create_branch(branch_data, created_by_id)
        data = branch.model_dump() if hasattr(branch, "model_dump") else branch.__dict__
        # add status string for convenience
        data.setdefault("status", "ACTIVE" if data.get("isActive") else "INACTIVE")
        return BranchResponseSchema(**data)
    
    async def get_branch(self, branch_id: int) -> Optional[BranchDetailResponseSchema]:
        """Get branch by ID with details."""
        branch = await self.branch_model.get_branch(branch_id)
        if not branch:
            return None

        # Calculate additional stats
        total_users = await self.db.user.count(where={"branchId": branch_id})
        active_users = await self.db.user.count(
            where={"branchId": branch_id, "isActive": True}
        )

        # Calculate sales stats for the branch
        total_sales_result = await self.db.sale.group_by(
            by=["branchId"],
            where={"branchId": branch_id},
            sum={"totalAmount": True}
        )
        total_sales = Decimal(
            str(
                getattr(
                    total_sales_result[0].sum,
                    "totalAmount",
                    getattr(total_sales_result[0].sum, "total_amount", 0),
                )
            )
        ) if total_sales_result else Decimal('0')

        # Current month sales
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_sales_result = await self.db.sale.group_by(
            by=["branchId"],
            where={
                "branchId": branch_id,
                "createdAt": {"gte": month_start}
            },
            sum={"totalAmount": True}
        )
        monthly_sales = Decimal(
            str(
                getattr(
                    monthly_sales_result[0].sum,
                    "totalAmount",
                    getattr(monthly_sales_result[0].sum, "total_amount", 0),
                )
            )
        ) if monthly_sales_result else Decimal('0')

        branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch.__dict__
        branch_dict.update({
            "total_users": total_users,
            "active_users": active_users,
            "total_sales": total_sales,
            "monthly_sales": monthly_sales,
            "created_by_name": None
        })

        return BranchDetailResponseSchema(**branch_dict)
    
    async def list_branches(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> BranchListResponseSchema:
        """Get paginated list of branches."""
        skip = (page - 1) * size
        branches, total = await self.branch_model.get_branches(
            skip=skip, limit=size, filters=filters
        )

        pages = (total + size - 1) // size

        branch_responses = []
        for branch in branches:
            branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch.__dict__
            branch_dict.setdefault("status", "ACTIVE" if branch_dict.get("isActive") else "INACTIVE")
            branch_responses.append(BranchResponseSchema(**branch_dict))

        return BranchListResponseSchema(
            branches=branch_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    async def update_branch(
        self,
        branch_id: int,
        branch_data: BranchUpdateSchema
    ) -> BranchResponseSchema:
        """Update branch."""
        # Check if branch exists
        existing_branch = await self.branch_model.get_branch(branch_id)
        if not existing_branch:
            # Use message arg; provide resource for context
            raise NotFoundError(
                "Branch not found",
                resource="branch"
            )

        # Check for name conflicts if name is being updated
        if branch_data.name and branch_data.name != existing_branch.name:
            name_conflict = await self.db.branch.find_first(
                where={
                    "name": branch_data.name,
                    "id": {"not": branch_id}
                }
            )
            if name_conflict:
                raise AlreadyExistsError(
                    "Branch with this name already exists",
                    details={"code": "BRANCH_NAME_EXISTS"}
                )

        branch = await self.branch_model.update_branch(branch_id, branch_data)
        return BranchResponseSchema.model_validate(branch)
    
    async def delete_branch(self, branch_id: int) -> bool:
        """Delete branch."""
        # Check if branch exists
        existing_branch = await self.branch_model.get_branch(branch_id)
        if not existing_branch:
            raise NotFoundError(
                "Branch not found",
                resource="branch"
            )

        try:
            success = await self.branch_model.delete_branch(branch_id)
            return success
        except ValueError as e:
            # business rule violation
            raise BusinessRuleError(str(e), details={"code": "BRANCH_DELETION_RESTRICTED"})
    
    async def get_branch_statistics(self) -> BranchStatsSchema:
        """Get branch statistics."""
        stats = await self.branch_model.get_branch_stats()
        return BranchStatsSchema(**stats)
    
    async def bulk_update_branches(
        self,
        bulk_data: BulkBranchUpdateSchema
    ) -> BulkOperationResponseSchema:
        """Bulk update branches."""
        result = await self.branch_model.bulk_update_branches(
            bulk_data.branch_ids, bulk_data.updates
        )
        return BulkOperationResponseSchema(**result)
    
    async def bulk_update_status(
        self,
        bulk_data: BulkBranchStatusUpdateSchema
    ) -> BulkOperationResponseSchema:
        """Bulk update branch status."""
        from app.modules.branches.schema import BranchUpdateSchema
        updates = BranchUpdateSchema(status=bulk_data.status)

        result = await self.branch_model.bulk_update_branches(
            bulk_data.branch_ids, updates
        )
        return BulkOperationResponseSchema(**result)

# Service factory function
def create_branch_service(db: Prisma) -> BranchService:
    """Create branch service instance."""
    return BranchService(db)
