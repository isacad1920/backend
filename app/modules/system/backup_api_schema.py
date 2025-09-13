"""Pydantic schemas for Backup API (aligned with current Prisma model)."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class BackupCreateRequest(BaseModel):
    """Request body for creating a backup."""
    type: Literal["FULL", "INCREMENTAL", "FILES", "DB"] = Field(..., description="Backup type")
    location: Optional[str] = Field(None, description="Target directory or storage URI")


class BackupResponse(BaseModel):
    """Response model for a backup record."""
    id: int
    type: str
    location: str
    file_name: Optional[str] = Field(None, alias="fileName")
    size_mb: Optional[float] = Field(None, alias="sizeMB")
    status: str
    error_log: Optional[str] = Field(None, alias="errorLog")
    created_by_id: Optional[int] = Field(None, alias="createdById")
    created_at: datetime = Field(alias="createdAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class BackupStats(BaseModel):
    total: int
    successful: int
    failed: int
    pending: int
    total_size_mb: float
    last_backup_at: Optional[datetime]


class BackupRestoreResponse(BaseModel):
    backup_id: int = Field(alias="backupId")
    mode: str
    dry_run: bool = Field(alias="dryRun")
    restored_tables: List[str] = Field(default_factory=list)
    skipped_tables: List[str] = Field(default_factory=list)
    message: str
