# Planning Poker

A real-time planning poker application for agile scrum teams, built with React, TypeScript, FastAPI, and WebSockets.

## Features

- Create and join ephemeral rooms with unique room codes
- Real-time voting with WebSocket communication
- Standard Fibonacci sequence cards (0, 1, 2, 3, 5, 8, 13, 21, ?, ☕)
- Facilitator controls for revealing votes and resetting rounds
- Clean, minimal UI with Tailwind CSS
- No authentication required - just enter your name and start voting

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for styling
- **Socket.IO Client** for WebSocket communication
- **React Router** for navigation

### Backend
- **FastAPI** with Python 3.11
- **python-socketio** for WebSocket server
- **Redis** for ephemeral room storage
- **Pydantic** for data validation

## Prerequisites

- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development without Docker

## Quick Start

1. Clone the repository:
   ```bash
   cd planning-poker
   ```

2. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8008
   - **API Documentation**: http://localhost:8008/docs

4. View logs:
   ```bash
   docker-compose logs -f
   ```

5. Stop services:
   ```bash
   docker-compose down
   ```

## Development

### Backend Development

```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest

# Check logs
docker-compose logs -f backend
```

### Frontend Development

```bash
# Enter frontend container
docker-compose exec frontend sh

# Install new dependency
npm install <package-name>

# Check logs
docker-compose logs -f frontend
```

### Hot Reload

Both frontend and backend are configured with hot reload:
- Frontend: Vite HMR updates automatically on file changes
- Backend: Uvicorn reloads on Python file changes

### Reset Redis Data

```bash
docker-compose down -v
docker-compose up -d
```

## Project Structure

```
planning-poker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Pydantic data models
│   │   ├── services/            # Business logic
│   │   └── websocket/           # WebSocket handlers
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── contexts/            # React contexts
│   │   ├── pages/               # Page components
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utilities
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## How to Use

1. **Create a Room**:
   - Enter your name on the home page
   - Click "Create New Room"
   - Share the room code with your team

2. **Join a Room**:
   - Enter your name and the room code
   - Click "Join Room"

3. **Vote**:
   - Select a card to submit your vote
   - Other participants will see that you voted (but not your value)

4. **Reveal Votes** (Facilitator only):
   - Once everyone has voted, click "Reveal Votes"
   - See all votes and the average

5. **Start New Round** (Facilitator only):
   - Click "Start New Round" to clear all votes
   - Continue with the next story

## Environment Variables

### Backend (.env)
```
REDIS_HOST=redis
REDIS_PORT=6379
ROOM_TTL=86400
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8008
VITE_WS_URL=http://localhost:8008
```

## Production Deployment

### Frontend (Static Site)
Build the frontend for production:
```bash
cd frontend
npm run build
```

Deploy the `dist/` folder to S3 + CloudFront or any static hosting service.

### Backend (AWS)
Options for deploying the backend:
- **ECS/Fargate**: Container-based deployment
- **EC2**: Traditional server deployment
- **Lambda**: Serverless (requires adapter)

Use **ElastiCache** for Redis in production.

Infrastructure as Code with **Terraform** can be added later.

## API Endpoints

### HTTP
- `GET /health` - Health check

### WebSocket Events

**Client → Server**:
- `join_room(room_code, user_name)` - Join/create room
- `submit_vote(vote)` - Submit vote
- `reveal_votes()` - Reveal all votes (facilitator)
- `reset_round()` - Start new round (facilitator)

**Server → Client**:
- `room_joined(room_code, user_id, is_facilitator)` - Join confirmation
- `room_state(Room)` - Full room state
- `user_joined(user)` / `user_left(user_id)` - User events
- `vote_submitted(user_id)` - Vote notification
- `votes_revealed(votes)` - Revealed votes
- `round_reset(round)` - Round reset

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
