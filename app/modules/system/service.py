"""
SystemInfo service layer for business logic.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from generated.prisma import Prisma
from generated.prisma.models import SystemInfo
from app.db import prisma
from app.core.exceptions import (
    ValidationError, NotFoundError, DatabaseError, AuthorizationError
)
from app.modules.system.schema import (
    SystemInfoSchema, SystemInfoUpdateSchema, SystemInfoResponseSchema
)

logger = logging.getLogger(__name__)


class SystemService:
    """Service for managing system information."""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def get_system_info(
        self, 
        current_user = None
    ) -> Optional[SystemInfoResponseSchema]:
        """Get current system information."""
        try:
            # Check permissions
            if not current_user or current_user.role not in ['ADMIN', 'MANAGER']:
                raise AuthorizationError("Insufficient permissions to view system info")
            
            # Get system info (there should only be one record)
            system_info = await self.db.systeminfo.find_first()
            
            if not system_info:
                return None
                
            return SystemInfoResponseSchema.model_validate(system_info)
            
        except AuthorizationError:
            raise
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            raise DatabaseError("Failed to retrieve system information")
    
    async def create_system_info(
        self,
        system_data: SystemInfoSchema,
        current_user = None
    ) -> SystemInfoResponseSchema:
        """Create system information (only if none exists)."""
        try:
            # Only admins can create system info
            if not current_user or current_user.role != 'ADMIN':
                raise AuthorizationError("Only admins can create system information")
            
            # Check if system info already exists
            existing = await self.db.systeminfo.find_first()
            if existing:
                raise ValidationError("System information already exists. Use update instead.")
            
            # Create system info
            system_info = await self.db.systeminfo.create(
                data={
                    "systemName": system_data.system_name,
                    "version": system_data.version,
                    "environment": system_data.environment.value,
                    "companyName": system_data.company_name,
                    "companyEmail": system_data.company_email,
                    "companyPhone": system_data.company_phone,
                    "companyAddress": system_data.company_address,
                    "baseCurrency": system_data.base_currency.value,
                    "timezone": system_data.timezone
                }
            )
            
            logger.info(f"System info created by user {current_user.id}")
            return SystemInfoResponseSchema.model_validate(system_info)
            
        except (ValidationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to create system info: {e}")
            raise DatabaseError("Failed to create system information")
    
    async def update_system_info(
        self,
        system_data: SystemInfoUpdateSchema,
        current_user = None
    ) -> SystemInfoResponseSchema:
        """Update system information."""
        try:
            # Only admins can update system info
            if not current_user or current_user.role != 'ADMIN':
                raise AuthorizationError("Only admins can update system information")
            
            # Find existing system info
            existing = await self.db.systeminfo.find_first()
            if not existing:
                raise NotFoundError("System information not found. Create it first.")
            
            # Prepare update data (only include non-None values)
            update_data = {}
            if system_data.system_name is not None:
                update_data["systemName"] = system_data.system_name
            if system_data.version is not None:
                update_data["version"] = system_data.version
            if system_data.environment is not None:
                update_data["environment"] = system_data.environment.value
            if system_data.company_name is not None:
                update_data["companyName"] = system_data.company_name
            if system_data.company_email is not None:
                update_data["companyEmail"] = system_data.company_email
            if system_data.company_phone is not None:
                update_data["companyPhone"] = system_data.company_phone
            if system_data.company_address is not None:
                update_data["companyAddress"] = system_data.company_address
            if system_data.base_currency is not None:
                update_data["baseCurrency"] = system_data.base_currency.value
            if system_data.timezone is not None:
                update_data["timezone"] = system_data.timezone
            
            if not update_data:
                raise ValidationError("No fields provided to update")
            
            update_data["updatedAt"] = datetime.utcnow()
            
            # Update system info
            system_info = await self.db.systeminfo.update(
                where={"id": existing.id},
                data=update_data
            )
            
            logger.info(f"System info updated by user {current_user.id}")
            return SystemInfoResponseSchema.model_validate(system_info)
            
        except (ValidationError, NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to update system info: {e}")
            raise DatabaseError("Failed to update system information")
    
    async def initialize_default_system_info(self) -> SystemInfoResponseSchema:
        """Initialize system info with default values if none exists."""
        try:
            # Check if system info already exists
            existing = await self.db.systeminfo.find_first()
            if existing:
                return SystemInfoResponseSchema.model_validate(existing)
            
            # Create default system info
            default_data = SystemInfoSchema(
                system_name="SOFinance POS System",
                version="1.0.0",
                environment="DEV",
                company_name="Default Company",
                base_currency="USD",
                timezone="UTC"
            )
            
            system_info = await self.db.systeminfo.create(
                data={
                    "systemName": default_data.system_name,
                    "version": default_data.version,
                    "environment": default_data.environment.value,
                    "companyName": default_data.company_name,
                    "companyEmail": default_data.company_email,
                    "companyPhone": default_data.company_phone,
                    "companyAddress": default_data.company_address,
                    "baseCurrency": default_data.base_currency.value,
                    "timezone": default_data.timezone
                }
            )
            
            logger.info("Default system info initialized")
            return SystemInfoResponseSchema.model_validate(system_info)
            
        except Exception as e:
            logger.error(f"Failed to initialize default system info: {e}")
            raise DatabaseError("Failed to initialize system information")


# Utility function for main.py usage
async def get_system_info() -> Optional[SystemInfo]:
    """
    Fetch the first SystemInfo record from the database for main.py usage.
    Returns None if no record exists.
    """
    return await prisma.systeminfo.find_first()
