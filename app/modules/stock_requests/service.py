"""
Stock request service layer.
"""
import logging
from typing import List, Dict, Any, Optional
from app.core.stock_requests import stock_request_service
from app.modules.stock_requests.schema import (
    CreateStockRequestSchema, ApproveStockRequestSchema,
    ShipStockRequestSchema, ReceiveStockRequestSchema,
    StockRequestResponseSchema
)

logger = logging.getLogger(__name__)


class StockRequestService:
    """Service for managing stock requests."""
    
    def __init__(self):
        """Initialize the stock request service."""
        self.core_service = stock_request_service
    
    async def create_stock_request(
        self, 
        request_data: CreateStockRequestSchema, 
        current_user
    ) -> StockRequestResponseSchema:
        """Create a new stock request."""
        try:
            # Prepare items data
            items_data = []
            for item in request_data.items:
                items_data.append({
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "current_stock": item.current_stock,
                    "reason": item.reason
                })
            
            request_id = await self.core_service.create_request(
                requester_id=int(current_user.id),
                requester_name=current_user.username,
                requester_branch=current_user.branch_id,
                items=items_data,
                priority=request_data.priority,
                notes=request_data.notes
            )
            
            # Get the created request to return
            created_request = self.core_service.get_request(request_id)
            return StockRequestResponseSchema.model_validate(created_request.to_dict())
        except Exception as e:
            logger.error(f"Error creating stock request: {e}")
            raise
    
    async def get_stock_requests(
        self, 
        status_filter: Optional[str] = None,
        from_branch_id: Optional[int] = None,
        to_branch_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[StockRequestResponseSchema]:
        """Get stock requests with filtering."""
        try:
            # Get all requests from the core service
            all_requests = list(self.core_service.requests.values())
            
            # Filter by status if provided
            if status_filter:
                all_requests = [req for req in all_requests if req.status.value == status_filter]
            
            # Filter by from_branch_id if provided
            if from_branch_id:
                all_requests = [req for req in all_requests if req.branch_id == str(from_branch_id)]
            
            # Filter by to_branch_id if provided - this would need destination branch field
            # For now, we'll skip this filter as it's not in the current model
            
            # Apply pagination
            paginated_requests = all_requests[offset:offset + limit]
                
            return [StockRequestResponseSchema.model_validate(req.to_dict()) for req in paginated_requests]
        except Exception as e:
            logger.error(f"Error getting stock requests: {e}")
            raise
    
    async def approve_stock_request(
        self,
        request_id: str,
        approval_data: ApproveStockRequestSchema,
        current_user
    ) -> StockRequestResponseSchema:
        """Approve a stock request."""
        try:
            result = await self.core_service.approve_request(
                request_id=request_id,
                approver_id=int(current_user.id),
                approver_name=current_user.username,
                approved_items=approval_data.approved_items,
                notes=approval_data.notes
            )
            return StockRequestResponseSchema.model_validate(result.to_dict())
        except Exception as e:
            logger.error(f"Error approving stock request: {e}")
            raise
