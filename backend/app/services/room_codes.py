import random
from app.services.redis_service import redis_service

# Character set excluding ambiguous characters (0, O, 1, I)
CHARSET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def generate_room_code(length: int = 6) -> str:
    """
    Generate a unique room code.

    Args:
        length: Length of the room code (default 6)

    Returns:
        A unique room code that doesn't exist in Redis
    """
    max_attempts = 10

    for _ in range(max_attempts):
        code = ''.join(random.choices(CHARSET, k=length))
        # Check if code already exists
        if not redis_service.exists(f"room:{code}"):
            return code

    # If we still have collisions after max_attempts, increase length
    return generate_room_code(length + 1)


def validate_room_code(code: str) -> bool:
    """
    Validate a room code format.

    Args:
        code: The room code to validate

    Returns:
        True if valid, False otherwise
    """
    if not code or len(code) < 6:
        return False

    # Check if all characters are in allowed charset
    return all(c in CHARSET for c in code.upper())
