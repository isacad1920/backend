"""
SystemInfo Pydantic schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum

from pydantic import Field, validator

from app.core.base_schema import ApiBaseModel


class Environment(str, Enum):
    """System environment enum."""
    DEV = "DEV"
    STAGING = "STAGING" 
    PROD = "PROD"


class Currency(str, Enum):
    """Currency enum."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    SOS = "SOS"  # Somali Shilling
    ETB = "ETB"  # Ethiopian Birr


class SystemInfoSchema(ApiBaseModel):
    """Base schema for system info."""
    system_name: str = Field(..., min_length=1, max_length=100, description="System name")
    version: str | None = Field(None, max_length=20, description="System version")
    environment: Environment = Field(..., description="System environment")
    company_name: str | None = Field(None, max_length=200, description="Company name") 
    company_email: str | None = Field(None, max_length=100, description="Company email")
    company_phone: str | None = Field(None, max_length=20, description="Company phone")
    company_address: str | None = Field(None, max_length=500, description="Company address")
    base_currency: Currency = Field(..., description="Base currency")
    timezone: str | None = Field(None, max_length=50, description="System timezone")
    
    @validator('company_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if v:
            # Basic timezone validation
            valid_timezones = [
                'UTC', 'Africa/Mogadishu', 'Africa/Nairobi', 'Africa/Addis_Ababa',
                'America/New_York', 'Europe/London', 'Asia/Dubai'
            ]
            if v not in valid_timezones:
                raise ValueError(f'Timezone must be one of: {", ".join(valid_timezones)}')
        return v

    class Config:
        from_attributes = True


class SystemInfoUpdateSchema(ApiBaseModel):
    """Schema for updating system info."""
    system_name: str | None = Field(None, min_length=1, max_length=100)
    version: str | None = Field(None, max_length=20)
    environment: Environment | None = None
    company_name: str | None = Field(None, max_length=200)
    company_email: str | None = Field(None, max_length=100)
    company_phone: str | None = Field(None, max_length=20) 
    company_address: str | None = Field(None, max_length=500)
    base_currency: Currency | None = None
    timezone: str | None = Field(None, max_length=50)
    
    @validator('company_email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    class Config:
        from_attributes = True


class SystemInfoResponseSchema(ApiBaseModel):
    """Schema for system info response."""
    id: int
    system_name: str = Field(alias="systemName")
    version: str | None = Field(None, alias="version")
    environment: Environment = Field(alias="environment")
    company_name: str | None = Field(None, alias="companyName")
    company_email: str | None = Field(None, alias="companyEmail")
    company_phone: str | None = Field(None, alias="companyPhone")
    company_address: str | None = Field(None, alias="companyAddress")
    base_currency: Currency = Field(alias="baseCurrency")
    timezone: str | None = Field(None, alias="timezone")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class BackupType(str, Enum):
    """Unified backup type enum (aligned with Prisma model)."""
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    FILES = "FILES"
    DB = "DB"


class BackupStatus(str, Enum):
    """Unified backup status enum (Prisma model)."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BackupSchema(ApiBaseModel):
    """Schema for creating a backup via API (request body)."""
    type: BackupType = Field(..., description="Type of backup: FULL, INCREMENTAL, FILES, DB")
    location: str | None = Field(None, max_length=500, description="Target path or storage URI")

    class Config:
        from_attributes = True


class BackupResponseSchema(ApiBaseModel):
    """Schema for returning a backup record."""
    id: int
    type: BackupType
    location: str
    file_name: str | None = Field(None, alias="fileName")
    size_mb: float | None = Field(None, alias="sizeMB")
    status: BackupStatus
    error_log: str | None = Field(None, alias="errorLog")
    created_by_id: int | None = Field(None, alias="createdById")
    created_at: datetime = Field(alias="createdAt")
    completed_at: datetime | None = Field(None, alias="completedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class BackupStatsSchema(ApiBaseModel):
    total: int
    successful: int
    failed: int
    pending: int
    total_size_mb: float
    last_backup_at: datetime | None


class BackupRestoreResultSchema(ApiBaseModel):
    backup_id: int = Field(alias="backupId")
    mode: str
    dry_run: bool = Field(alias="dryRun")
    restored_tables: list[str]
    skipped_tables: list[str]
    message: str
