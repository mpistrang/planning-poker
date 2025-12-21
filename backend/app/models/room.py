from pydantic import BaseModel
from typing import Dict, List, Optional
from app.models.user import User


class VoteHistory(BaseModel):
    round: int
    votes: Dict[str, str]
    revealed_at: str


class Room(BaseModel):
    room_code: str
    created_at: str
    state: str = "voting"  # "voting" or "revealed"
    current_round: int = 1
    users: Dict[str, User] = {}
    vote_history: List[VoteHistory] = []

    class Config:
        json_schema_extra = {
            "example": {
                "room_code": "ABCD12",
                "created_at": "2025-12-20T10:00:00Z",
                "state": "voting",
                "current_round": 1,
                "users": {
                    "user_123": {
                        "id": "user_123",
                        "name": "Alice",
                        "connected": True,
                        "is_facilitator": True,
                        "current_vote": None,
                        "joined_at": "2025-12-20T10:00:00Z"
                    }
                },
                "vote_history": []
            }
        }
