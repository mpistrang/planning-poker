import socketio
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Create Socket.IO server with CORS
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.cors_origins_list,
    logger=settings.environment == "development",
    engineio_logger=settings.environment == "development"
)

# Socket.IO ASGI app
socket_app = socketio.ASGIApp(
    sio,
    socketio_path='socket.io'
)

logger.info("Socket.IO server initialized")
