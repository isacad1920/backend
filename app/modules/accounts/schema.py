from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

class AccountBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    type: str = Field(..., description="Account type enum value")
    currency: str = Field("USD", description="Currency code")
    branch_id: Optional[int] = Field(None, description="Owning branch ID")

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)

class AccountOut(BaseModel):
    id: int
    name: str
    type: str
    currency: str
    balance: str
    active: bool
    branch_id: Optional[int] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

class AccountList(BaseModel):
    items: list[AccountOut]
    total: int
    page: int
    limit: int
