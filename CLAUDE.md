# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A real-time planning poker application for agile scrum teams. The application uses WebSockets for real-time communication, ephemeral Redis storage for rooms, and a clean React frontend with Tailwind CSS.

## Architecture

### High-Level Structure

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 + python-socketio
- **Storage**: Redis (ephemeral, 24-hour TTL)
- **Communication**: WebSockets via Socket.IO
- **Deployment**: Docker Compose for local dev

### Backend Architecture

**Entry Point**: `backend/app/main.py`
- Mounts Socket.IO app at root path
- Imports event handlers on startup
- Configures CORS for frontend

**WebSocket Events**: `backend/app/websocket/events.py` (CRITICAL FILE)
- Handles all real-time events: join_room, submit_vote, reveal_votes, reset_round
- Maintains session mapping (socket_id -> {room_code, user_id})
- Broadcasts updates to room participants

**Room Service**: `backend/app/services/room_service.py` (CRITICAL FILE)
- Business logic for room operations
- Room CRUD operations in Redis
- User management within rooms
- First user = facilitator, reassigned if they leave

**Data Models**: `backend/app/models/`
- `room.py`: Room state, vote history
- `user.py`: User data, vote status
- Pydantic models for validation

**Redis Service**: `backend/app/services/redis_service.py`
- Abstraction over Redis client
- JSON serialization/deserialization
- Connection health checks

### Frontend Architecture

**Context Providers**: (CRITICAL PATTERN)
- `SocketContext`: Manages Socket.IO connection, provides socket instance
- `RoomContext`: Manages room state, listens to WebSocket events, provides actions

**State Management**:
- Room state synced via WebSocket events
- Optimistic updates on user actions
- No Redux - Context API sufficient for this app size

**Key Components**:
- `Room.tsx`: Main voting page (CRITICAL FILE)
- `CardSelector.tsx`: Fibonacci card grid
- `VotingStatus.tsx`: Shows who voted (not values until revealed)
- `VoteResults.tsx`: Displays revealed votes and average
- `RoomControls.tsx`: Facilitator controls (reveal/reset)

**Routing**:
- `/`: Home page (create/join room)
- `/room/:roomCode?name=...`: Room page (voting interface)

### Data Flow

1. **Join Room**:
   - Frontend emits `join_room` event
   - Backend creates room if doesn't exist, adds user
   - First user gets `is_facilitator: true`
   - Backend emits `room_joined` and `room_state` to user
   - Backend broadcasts `user_joined` to other participants

2. **Submit Vote**:
   - Frontend emits `submit_vote` with vote value
   - Backend stores vote in Redis (not revealed)
   - Backend broadcasts `vote_submitted` with user_id (no value)
   - UI shows checkmark for voted users

3. **Reveal Votes**:
   - Facilitator emits `reveal_votes`
   - Backend changes room state to "revealed"
   - Backend broadcasts `votes_revealed` with all votes
   - Frontend displays votes and calculates average

4. **Reset Round**:
   - Facilitator emits `reset_round`
   - Backend clears all votes, increments round number
   - Backend broadcasts `round_reset`
   - Frontend clears UI

### Redis Schema

**Room Key**: `room:{room_code}` (TTL: 24 hours)
```json
{
  "room_code": "ABCD12",
  "state": "voting",  // or "revealed"
  "current_round": 1,
  "users": {
    "user_id": {
      "id": "user_id",
      "name": "Alice",
      "is_facilitator": true,
      "current_vote": "5"
    }
  }
}
```

**Room Codes**: 6-character alphanumeric (uppercase), excluding ambiguous chars (0,O,1,I)

## Development Commands

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild After Changes
```bash
docker-compose up -d --build
```

### Stop Services
```bash
docker-compose down
```

### Reset Redis Data
```bash
docker-compose down -v
```

### Backend Shell
```bash
docker-compose exec backend bash
```

### Frontend Shell
```bash
docker-compose exec frontend sh
```

### Run Backend Tests
```bash
docker-compose exec backend pytest
```

### Install Frontend Dependency
```bash
docker-compose exec frontend npm install <package>
```

## Ports

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8008
- **API Docs**: http://localhost:8008/docs
- **Redis**: Internal only (not exposed)

## Important Implementation Notes

### WebSocket Event Handling
- All events use Pydantic schemas for validation (backend/app/websocket/schemas.py)
- Session management tracks socket_id -> {room_code, user_id}
- Reconnection handled automatically by Socket.IO client

### Vote Privacy
- During voting: only user_id broadcast (not vote value)
- After reveal: full votes object broadcast to all users
- Frontend shows checkmark for voted users before reveal

### Facilitator Role
- First user in room becomes facilitator
- If facilitator leaves, next user becomes facilitator
- Only facilitator can reveal votes or reset rounds

### Error Handling
- Backend emits `error` event with message
- Frontend displays error banner at top of room
- Connection status shown in header

## Common Tasks

### Add New WebSocket Event
1. Add schema to `backend/app/websocket/schemas.py`
2. Add handler to `backend/app/websocket/events.py`
3. Add TypeScript types to `frontend/src/types/events.ts`
4. Add listener in `RoomContext.tsx`
5. Update UI components as needed

### Add New Card Value
1. Update `CARD_VALUES` in `frontend/src/utils/constants.ts`
2. Update `VALID_VOTES` in `backend/app/websocket/events.py`

### Change Room TTL
Update `ROOM_TTL` in `backend/.env` (default: 86400 seconds = 24 hours)

### Add Persistent Storage
Replace Redis service with PostgreSQL or similar, update `room_service.py` to use ORM instead of Redis client.
