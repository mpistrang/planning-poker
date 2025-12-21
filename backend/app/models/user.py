from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: str
    name: str
    connected: bool = True
    is_facilitator: bool = False
    current_vote: Optional[str] = None
    joined_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "name": "Alice",
                "connected": True,
                "is_facilitator": True,
                "current_vote": "5",
                "joined_at": "2025-12-20T10:00:00Z"
            }
        }
