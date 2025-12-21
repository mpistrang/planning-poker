from pydantic import BaseModel
from typing import Optional, Dict


class JoinRoomData(BaseModel):
    room_code: str
    user_name: str


class SubmitVoteData(BaseModel):
    vote: str


class ErrorData(BaseModel):
    message: str
    code: Optional[str] = None


class RoomJoinedData(BaseModel):
    room_code: str
    user_id: str
    is_facilitator: bool


class UserData(BaseModel):
    user_id: str
    user_name: str


class VoteSubmittedData(BaseModel):
    user_id: str


class VotesRevealedData(BaseModel):
    votes: Dict[str, str]


class RoundResetData(BaseModel):
    round: int


class KickUserData(BaseModel):
    user_id: str


class UserKickedData(BaseModel):
    user_id: str
    kicked_by: str
