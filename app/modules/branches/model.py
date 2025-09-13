"""
Branch database operations and models.
"""
import logging
from typing import Any

from app.modules.branches.schema import BranchCreateSchema, BranchUpdateSchema
from generated.prisma import Prisma
from generated.prisma.models import Branch

logger = logging.getLogger(__name__)

class BranchModel:
    """Branch model class for database operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create_branch(
        self, 
        branch_data: BranchCreateSchema, 
        created_by_id: int | None = None
    ) -> Branch:
        """Create a new branch."""
        try:
            data = branch_data.model_dump(exclude_unset=True)
            # Remove non-persisted fields
            data.pop("email", None)
            # Normalize possible aliases
            if "status" in data and "isActive" not in data:
                status_val = str(data.pop("status"))
                data["isActive"] = True if status_val.upper() == "ACTIVE" else False
            if created_by_id:
                data["created_by_id"] = created_by_id
                
            branch = await self.db.branch.create(data=data)
            logger.info(f"Created branch: {branch.id}")
            return branch
            
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise
    
    async def get_branch(self, branch_id: int) -> Branch | None:
        """Get branch by ID."""
        try:
            branch = await self.db.branch.find_unique(
                where={"id": branch_id}
            )
            return branch
            
        except Exception as e:
            logger.error(f"Error getting branch {branch_id}: {str(e)}")
            raise
    
    async def get_branches(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[Branch], int]:
        """Get paginated list of branches."""
        try:
            where_conditions = {}
            
            if filters:
                if filters.get("search"):
                    search_term = filters["search"]
                    where_conditions["OR"] = [
                        {"name": {"contains": search_term, "mode": "insensitive"}},
                        {"address": {"contains": search_term, "mode": "insensitive"}},
                    ]
                
                if filters.get("name"):
                    where_conditions["name"] = {"contains": filters["name"], "mode": "insensitive"}
                
                if filters.get("isActive") is not None:
                    where_conditions["isActive"] = filters["isActive"]
            
            # Get total count
            total = await self.db.branch.count(where=where_conditions)
            
            # Get branches
            branches = await self.db.branch.find_many(
                where=where_conditions,
                skip=skip,
                take=limit,
                order={"createdAt": "desc"}
            )
            
            return branches, total
            
        except Exception as e:
            logger.error(f"Error getting branches: {str(e)}")
            raise
    
    async def update_branch(
        self, 
        branch_id: int, 
        branch_data: BranchUpdateSchema
    ) -> Branch | None:
        """Update branch."""
        try:
            data = branch_data.model_dump(exclude_unset=True)
            # Handle status -> isActive mapping and remove non-DB fields
            if "status" in data:
                status_val = str(data.pop("status")) if data["status"] is not None else None
                if status_val:
                    data["isActive"] = True if status_val.upper() == "ACTIVE" else False
            data.pop("email", None)
            data.pop("manager_name", None)
            if not data:
                return await self.get_branch(branch_id)
                
            branch = await self.db.branch.update(
                where={"id": branch_id},
                data=data
            )
            logger.info(f"Updated branch: {branch_id}")
            return branch
            
        except Exception as e:
            logger.error(f"Error updating branch {branch_id}: {str(e)}")
            raise
    
    async def delete_branch(self, branch_id: int) -> bool:
        """Delete branch."""
        try:
            # Check if branch has users
            users_count = await self.db.user.count(where={"branchId": branch_id})
            if users_count > 0:
                raise ValueError("Cannot delete branch with existing users")
            
            # Check if branch has sales
            sales_count = await self.db.sale.count(where={"branchId": branch_id})
            if sales_count > 0:
                raise ValueError("Cannot delete branch with existing sales records")
            
            await self.db.branch.delete(where={"id": branch_id})
            logger.info(f"Deleted branch: {branch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting branch {branch_id}: {str(e)}")
            raise
    
    async def get_branch_stats(self) -> dict[str, Any]:
        """Get branch statistics."""
        try:
            total_branches = await self.db.branch.count()
            
            active_branches = await self.db.branch.count(
                where={"isActive": True}
            )
            
            inactive_branches = await self.db.branch.count(
                where={"isActive": False}
            )
            
            # Top performing branches (by creation date)
            top_branches = await self.db.branch.find_many(
                take=5,
                order={"createdAt": "desc"}
            )
            
            top_performing = [
                {
                    "id": branch.id,
                    "name": branch.name,
                    "is_active": branch.isActive,
                    "created_at": branch.createdAt.isoformat()
                }
                for branch in top_branches
            ]
            
            return {
                "total_branches": total_branches,
                "active_branches": active_branches,
                "inactive_branches": inactive_branches,
                "top_performing_branches": top_performing
            }
            
        except Exception as e:
            logger.error(f"Error getting branch stats: {str(e)}")
            raise
    
    async def bulk_update_branches(
        self,
        branch_ids: list[int],
        updates: BranchUpdateSchema
    ) -> dict[str, Any]:
        """Bulk update branches."""
        try:
            data = updates.model_dump(exclude_unset=True)
            # Apply same normalization as single update
            if "status" in data:
                status_val = str(data.pop("status")) if data["status"] is not None else None
                if status_val:
                    data["isActive"] = True if status_val.upper() == "ACTIVE" else False
            data.pop("email", None)
            data.pop("manager_name", None)
            if not data:
                return {"success_count": 0, "error_count": 0, "errors": []}
            
            success_count = 0
            errors = []
            
            for branch_id in branch_ids:
                try:
                    await self.db.branch.update(
                        where={"id": branch_id},
                        data=data
                    )
                    success_count += 1
                except Exception as e:
                    errors.append(f"Branch {branch_id}: {str(e)}")
            
            error_count = len(branch_ids) - success_count
            logger.info(f"Bulk updated branches: {success_count} success, {error_count} errors")
            
            return {
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error in bulk update branches: {str(e)}")
            raise
