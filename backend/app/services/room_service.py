import uuid
import logging
from datetime import datetime
from typing import Optional, Dict
from app.models.room import Room, VoteHistory
from app.models.user import User
from app.services.redis_service import redis_service
from app.services.room_codes import generate_room_code
from app.config import settings

logger = logging.getLogger(__name__)


class RoomService:
    @staticmethod
    def create_room(room_code: Optional[str] = None) -> Room:
        """Create a new room with a unique room code or use provided code"""
        if not room_code:
            room_code = generate_room_code()
        else:
            # Check if room with this code already exists
            existing_room = RoomService.get_room(room_code)
            if existing_room:
                logger.info(f"Room {room_code} already exists, returning existing room")
                return existing_room

        now = datetime.utcnow().isoformat() + "Z"

        room = Room(
            room_code=room_code,
            created_at=now,
            state="voting",
            current_round=1,
            users={},
            vote_history=[]
        )

        # Save to Redis with TTL
        redis_service.set(f"room:{room_code}", room.model_dump(), ttl=settings.room_ttl)
        logger.info(f"Created room: {room_code}")

        return room

    @staticmethod
    def get_room(room_code: str) -> Optional[Room]:
        """Get room by code"""
        data = redis_service.get(f"room:{room_code}")
        if data:
            return Room(**data)
        return None

    @staticmethod
    def save_room(room: Room) -> bool:
        """Save room to Redis"""
        return redis_service.set(f"room:{room.room_code}", room.model_dump(), ttl=settings.room_ttl)

    @staticmethod
    def delete_room(room_code: str) -> bool:
        """Delete room from Redis"""
        return redis_service.delete(f"room:{room_code}")

    @staticmethod
    def add_user(room_code: str, user_name: str, user_id: Optional[str] = None) -> Optional[tuple[Room, User]]:
        """Add a user to a room or rejoin if user_id exists"""
        room = RoomService.get_room(room_code)
        if not room:
            return None

        now = datetime.utcnow().isoformat() + "Z"

        logger.info(f"add_user called: room_code={room_code}, user_name={user_name}, user_id={user_id}, current_users={len(room.users)}")

        # Check if user_id provided and exists in room (rejoining)
        if user_id and user_id in room.users:
            user = room.users[user_id]
            user.connected = True
            user.name = user_name  # Update name in case it changed
            RoomService.save_room(room)
            logger.info(f"User {user_name} ({user_id}) rejoined room {room_code}")
            return room, user

        # New user - generate new ID
        user_id = str(uuid.uuid4())

        # First user is facilitator
        is_facilitator = len(room.users) == 0

        logger.info(f"Creating new user: user_id={user_id}, is_facilitator={is_facilitator}, room has {len(room.users)} users")

        user = User(
            id=user_id,
            name=user_name,
            connected=True,
            is_facilitator=is_facilitator,
            current_vote=None,
            joined_at=now
        )

        room.users[user_id] = user
        RoomService.save_room(room)

        logger.info(f"User {user_name} ({user_id}) joined room {room_code}, now has {len(room.users)} users")
        return room, user

    @staticmethod
    def remove_user(room_code: str, user_id: str) -> Optional[Room]:
        """Remove a user from a room"""
        room = RoomService.get_room(room_code)
        if not room or user_id not in room.users:
            return None

        del room.users[user_id]

        # If no users left, delete room
        if not room.users:
            RoomService.delete_room(room_code)
            logger.info(f"Room {room_code} deleted (no users)")
            return None

        # If facilitator left, assign to next user
        has_facilitator = any(user.is_facilitator for user in room.users.values())
        if not has_facilitator and room.users:
            first_user_id = next(iter(room.users.keys()))
            room.users[first_user_id].is_facilitator = True

        RoomService.save_room(room)
        logger.info(f"User {user_id} removed from room {room_code}")
        return room

    @staticmethod
    def update_user_connection(room_code: str, user_id: str, connected: bool) -> Optional[Room]:
        """Update user connection status"""
        room = RoomService.get_room(room_code)
        if not room or user_id not in room.users:
            return None

        room.users[user_id].connected = connected
        RoomService.save_room(room)
        return room

    @staticmethod
    def submit_vote(room_code: str, user_id: str, vote: str) -> Optional[Room]:
        """Submit a vote for a user"""
        room = RoomService.get_room(room_code)
        if not room or user_id not in room.users:
            return None

        if room.state != "voting":
            logger.warning(f"Cannot vote in room {room_code} - state is {room.state}")
            return None

        room.users[user_id].current_vote = vote
        RoomService.save_room(room)
        logger.info(f"User {user_id} voted in room {room_code}")
        return room

    @staticmethod
    def clear_vote(room_code: str, user_id: str) -> Optional[Room]:
        """Clear a user's vote"""
        room = RoomService.get_room(room_code)
        if not room or user_id not in room.users:
            return None

        room.users[user_id].current_vote = None
        RoomService.save_room(room)
        return room

    @staticmethod
    def reveal_votes(room_code: str) -> Optional[Room]:
        """Reveal all votes in a room"""
        room = RoomService.get_room(room_code)
        if not room:
            return None

        room.state = "revealed"

        # Add to vote history
        votes = {user_id: user.current_vote for user_id, user in room.users.items() if user.current_vote}
        if votes:
            history = VoteHistory(
                round=room.current_round,
                votes=votes,
                revealed_at=datetime.utcnow().isoformat() + "Z"
            )
            room.vote_history.append(history)

        RoomService.save_room(room)
        logger.info(f"Votes revealed in room {room_code}")
        return room

    @staticmethod
    def reset_round(room_code: str) -> Optional[Room]:
        """Reset the round (clear all votes and increment round)"""
        room = RoomService.get_room(room_code)
        if not room:
            return None

        # Clear all votes
        for user in room.users.values():
            user.current_vote = None

        room.state = "voting"
        room.current_round += 1

        RoomService.save_room(room)
        logger.info(f"Round reset in room {room_code} (now round {room.current_round})")
        return room


room_service = RoomService()
