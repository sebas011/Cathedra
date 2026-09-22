from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas import GrantType

ReviewState = Literal["pending", "all"]


class GrantReviewRead(BaseModel):
    participation_id: int
    scholar_id: int
    scholar_name: str
    department: str | None
    program_name: str
    current_grant_type: GrantType | None
    original_grant_label: str
    standardized_at: datetime | None
    standardization_note: str | None


class GrantStandardizationUpdate(BaseModel):
    grant_type: GrantType
    note: str | None = Field(default=None, max_length=500)
