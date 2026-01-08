import logging
from typing import Dict
from app.websocket.manager import sio
from app.websocket.schemas import (
    JoinRoomData,
    SubmitVoteData,
    RoomJoinedData,
    UserData,
    VoteSubmittedData,
    VotesRevealedData,
    RoundResetData,
    ErrorData,
    KickUserData,
    UserKickedData
)
from app.services.room_service import room_service

logger = logging.getLogger(__name__)

# Store session data (socket_id -> {room_code, user_id})
sessions: Dict[str, Dict[str, str]] = {}

# Valid vote options
VALID_VOTES = {"0", ".5", "1", "2", "3", "5", "8", "13", "?", "☕"}


@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    sessions[sid] = {}
    await sio.emit('connect_success', to=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")

    # Get session data
    session = sessions.get(sid, {})
    room_code = session.get('room_code')
    user_id = session.get('user_id')

    if room_code and user_id:
        # Update user as disconnected
        room = room_service.update_user_connection(room_code, user_id, False)
        if room:
            await sio.emit('user_disconnected', {'user_id': user_id}, room=room_code, skip_sid=sid)

    # Clean up session
    if sid in sessions:
        del sessions[sid]


@sio.event
async def join_room(sid, data):
    """Handle user joining a room"""
    try:
        join_data = JoinRoomData(**data)
        room_code = join_data.room_code.upper()
        user_name = join_data.user_name.strip()

        if not user_name:
            await sio.emit('error', ErrorData(message="User name is required").model_dump(), to=sid)
            return

        # Check if room exists, if not create it with the provided code
        room = room_service.get_room(room_code)
        if not room:
            room = room_service.create_room(room_code)

        # Check if this is a rejoin (user_id exists in room)
        is_rejoining = join_data.user_id and room and join_data.user_id in room.users

        # Add user to room (or rejoin if user_id provided and exists)
        result = room_service.add_user(room_code, user_name, join_data.user_id)
        if not result:
            await sio.emit('error', ErrorData(message="Failed to join room").model_dump(), to=sid)
            return

        room, user = result

        # Store session data
        sessions[sid] = {
            'room_code': room_code,
            'user_id': user.id
        }

        # Join Socket.IO room
        await sio.enter_room(sid, room_code)

        # Send confirmation to user
        await sio.emit('room_joined', RoomJoinedData(
            room_code=room_code,
            user_id=user.id,
            is_facilitator=user.is_facilitator
        ).model_dump(), to=sid)

        # Send full room state to user
        await sio.emit('room_state', room.model_dump(), to=sid)

        # Only notify other users if this is a new join (not a rejoin)
        if not is_rejoining:
            await sio.emit('user_joined', {
                'user': user.model_dump()
            }, room=room_code, skip_sid=sid)
            logger.info(f"User {user_name} joined room {room_code}")
        else:
            logger.info(f"User {user_name} rejoined room {room_code}")

    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit('error', ErrorData(message=str(e)).model_dump(), to=sid)


@sio.event
async def leave_room(sid):
    """Handle user leaving a room"""
    try:
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        user_id = session.get('user_id')

        if not room_code or not user_id:
            return

        # Remove user from room
        room = room_service.remove_user(room_code, user_id)

        # Leave Socket.IO room
        await sio.leave_room(sid, room_code)

        # Notify other users
        if room:
            await sio.emit('user_left', {'user_id': user_id}, room=room_code)
            # Send updated room state
            await sio.emit('room_state', room.model_dump(), room=room_code)

        # Clear session
        sessions[sid] = {}

        logger.info(f"User {user_id} left room {room_code}")

    except Exception as e:
        logger.error(f"Error in leave_room: {e}")


@sio.event
async def submit_vote(sid, data):
    """Handle vote submission"""
    try:
        vote_data = SubmitVoteData(**data)
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        user_id = session.get('user_id')

        if not room_code or not user_id:
            await sio.emit('error', ErrorData(message="Not in a room").model_dump(), to=sid)
            return

        # Validate vote
        if vote_data.vote not in VALID_VOTES:
            await sio.emit('error', ErrorData(message="Invalid vote value").model_dump(), to=sid)
            return

        # Submit vote
        room = room_service.submit_vote(room_code, user_id, vote_data.vote)
        if not room:
            await sio.emit('error', ErrorData(message="Failed to submit vote").model_dump(), to=sid)
            return

        # Broadcast to room (without revealing the vote value)
        await sio.emit('vote_submitted', VoteSubmittedData(user_id=user_id).model_dump(), room=room_code)

        logger.info(f"User {user_id} voted in room {room_code}")

    except Exception as e:
        logger.error(f"Error in submit_vote: {e}")
        await sio.emit('error', ErrorData(message=str(e)).model_dump(), to=sid)


@sio.event
async def clear_vote(sid):
    """Handle clearing a vote"""
    try:
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        user_id = session.get('user_id')

        if not room_code or not user_id:
            return

        room = room_service.clear_vote(room_code, user_id)
        if room:
            await sio.emit('vote_cleared', {'user_id': user_id}, room=room_code)

    except Exception as e:
        logger.error(f"Error in clear_vote: {e}")


@sio.event
async def reveal_votes(sid):
    """Handle revealing votes"""
    try:
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        user_id = session.get('user_id')

        if not room_code or not user_id:
            await sio.emit('error', ErrorData(message="Not in a room").model_dump(), to=sid)
            return

        # Check if user is facilitator
        room = room_service.get_room(room_code)
        if not room or user_id not in room.users or not room.users[user_id].is_facilitator:
            await sio.emit('error', ErrorData(message="Only facilitator can reveal votes").model_dump(), to=sid)
            return

        # Reveal votes
        room = room_service.reveal_votes(room_code)
        if not room:
            await sio.emit('error', ErrorData(message="Failed to reveal votes").model_dump(), to=sid)
            return

        # Get votes and broadcast
        votes = {user_id: user.current_vote for user_id, user in room.users.items() if user.current_vote}
        await sio.emit('votes_revealed', VotesRevealedData(votes=votes).model_dump(), room=room_code)

        logger.info(f"Votes revealed in room {room_code}")

    except Exception as e:
        logger.error(f"Error in reveal_votes: {e}")
        await sio.emit('error', ErrorData(message=str(e)).model_dump(), to=sid)


@sio.event
async def reset_round(sid):
    """Handle resetting the round"""
    try:
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        user_id = session.get('user_id')

        if not room_code or not user_id:
            await sio.emit('error', ErrorData(message="Not in a room").model_dump(), to=sid)
            return

        # Check if user is facilitator
        room = room_service.get_room(room_code)
        if not room or user_id not in room.users or not room.users[user_id].is_facilitator:
            await sio.emit('error', ErrorData(message="Only facilitator can reset round").model_dump(), to=sid)
            return

        # Reset round
        room = room_service.reset_round(room_code)
        if not room:
            await sio.emit('error', ErrorData(message="Failed to reset round").model_dump(), to=sid)
            return

        # Broadcast reset
        await sio.emit('round_reset', RoundResetData(round=room.current_round).model_dump(), room=room_code)

        logger.info(f"Round reset in room {room_code} (now round {room.current_round})")

    except Exception as e:
        logger.error(f"Error in reset_round: {e}")
        await sio.emit('error', ErrorData(message=str(e)).model_dump(), to=sid)


@sio.event
async def kick_user(sid, data):
    """Handle kicking a user from the room (facilitator only)"""
    try:
        kick_data = KickUserData(**data)
        session = sessions.get(sid, {})
        room_code = session.get('room_code')
        kicker_id = session.get('user_id')

        if not room_code or not kicker_id:
            await sio.emit('error', ErrorData(message="Not in a room").model_dump(), to=sid)
            return

        # Check if user is facilitator
        room = room_service.get_room(room_code)
        if not room or kicker_id not in room.users or not room.users[kicker_id].is_facilitator:
            await sio.emit('error', ErrorData(message="Only facilitator can remove users").model_dump(), to=sid)
            return

        # Can't kick yourself
        if kick_data.user_id == kicker_id:
            await sio.emit('error', ErrorData(message="You cannot remove yourself").model_dump(), to=sid)
            return

        # Check if user exists in room
        if kick_data.user_id not in room.users:
            await sio.emit('error', ErrorData(message="User not found in room").model_dump(), to=sid)
            return

        # Find the socket_id of the user to kick
        kicked_socket_id = None
        for socket_id, sess_data in sessions.items():
            if sess_data.get('user_id') == kick_data.user_id and sess_data.get('room_code') == room_code:
                kicked_socket_id = socket_id
                break

        # Remove user from room
        room = room_service.remove_user(room_code, kick_data.user_id)

        # Notify the kicked user
        if kicked_socket_id:
            await sio.emit('user_kicked', UserKickedData(
                user_id=kick_data.user_id,
                kicked_by=kicker_id
            ).model_dump(), to=kicked_socket_id)

            # Leave Socket.IO room
            await sio.leave_room(kicked_socket_id, room_code)

            # Clear session
            if kicked_socket_id in sessions:
                sessions[kicked_socket_id] = {}

        # Broadcast to room that user was removed
        if room:
            await sio.emit('user_left', {'user_id': kick_data.user_id}, room=room_code)
            # Send updated room state
            await sio.emit('room_state', room.model_dump(), room=room_code)

        logger.info(f"User {kick_data.user_id} was kicked from room {room_code} by {kicker_id}")

    except Exception as e:
        logger.error(f"Error in kick_user: {e}")
        await sio.emit('error', ErrorData(message=str(e)).model_dump(), to=sid)
