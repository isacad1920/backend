"""
Base Pydantic model with project-wide settings for casing and ORM usage.
"""
from pydantic import BaseModel, ConfigDict

class ApiBaseModel(BaseModel):
    """Base model enforcing Option A conventions:
    - camelCase field names in code
    - snake_case aliases for wire format
    - accepts both camel and snake on input
    - supports from_attributes for Prisma ORM objects
    """
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    def dump_snake(self) -> dict:
        """Dump using field aliases (snake_case on wire)."""
        return self.model_dump(by_alias=True)

    @classmethod
    def from_orm_any(cls, obj):
        """Validate from Prisma objects or dicts safely."""
        return cls.model_validate(obj, from_attributes=True)
