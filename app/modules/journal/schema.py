"""
Journal Entry data models and schemas.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import Field, validator

from app.core.base_schema import ApiBaseModel


class JournalEntryLineSchema(ApiBaseModel):
    """Schema for individual journal entry line."""
    id: int | None = None
    account_id: int
    account_name: str | None = None
    account_code: str | None = None
    debit: Decimal = Field(default=Decimal('0'), decimal_places=2)
    credit: Decimal = Field(default=Decimal('0'), decimal_places=2)
    description: str | None = None

    class Config:
        from_attributes = True

    @validator('debit', 'credit')
    def validate_amounts(cls, v):
        """Ensure amounts are non-negative."""
        if v < 0:
            raise ValueError("Amounts must be non-negative")
        return v

class JournalEntryCreateSchema(ApiBaseModel):
    """Schema for creating a journal entry."""
    reference_type: str | None = Field(None, description="Type of business transaction")
    reference_id: int | None = Field(None, description="ID of the business record")
    lines: list[JournalEntryLineSchema] = Field(..., min_items=2)
    date: datetime | None = None

    @validator('lines')
    def validate_balanced_entry(cls, v):
        """Ensure debits equal credits."""
        total_debits = sum(line.debit for line in v)
        total_credits = sum(line.credit for line in v)
        
        if total_debits != total_credits:
            raise ValueError(f"Entry must be balanced: Debits ({total_debits}) != Credits ({total_credits})")
        
        if total_debits == 0:
            raise ValueError("Entry must have non-zero amounts")
        
        return v

    @validator('lines')
    def validate_line_amounts(cls, v):
        """Ensure each line has either debit OR credit (not both)."""
        for line in v:
            if line.debit > 0 and line.credit > 0:
                raise ValueError("A line cannot have both debit and credit amounts")
            if line.debit == 0 and line.credit == 0:
                raise ValueError("A line must have either a debit or credit amount")
        return v

class JournalEntryUpdateSchema(ApiBaseModel):
    """Schema for updating a journal entry."""
    reference_type: str | None = None
    reference_id: int | None = None
    lines: list[JournalEntryLineSchema] | None = None
    date: datetime | None = None

class JournalEntrySchema(ApiBaseModel):
    """Schema for journal entry response."""
    id: int
    reference_type: str | None
    reference_id: int | None
    date: datetime
    created_at: datetime
    updated_at: datetime
    lines: list[JournalEntryLineSchema]
    total_amount: Decimal
    is_balanced: bool

    class Config:
        from_attributes = True

class JournalEntryListSchema(ApiBaseModel):
    """Schema for paginated journal entry list."""
    entries: list[JournalEntrySchema]
    total: int
    page: int
    size: int
    pages: int

class TrialBalanceLineSchema(ApiBaseModel):
    """Schema for trial balance line item."""
    account_id: int
    account_name: str
    account_code: str
    account_type: str
    debit_balance: Decimal = Field(default=Decimal('0'))
    credit_balance: Decimal = Field(default=Decimal('0'))

    class Config:
        from_attributes = True

class TrialBalanceSchema(ApiBaseModel):
    """Schema for trial balance report."""
    as_of_date: datetime
    lines: list[TrialBalanceLineSchema]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool

    class Config:
        from_attributes = True
