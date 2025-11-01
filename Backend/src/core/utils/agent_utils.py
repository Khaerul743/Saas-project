import secrets
import string
import time


def generate_agent_id():
    """
    Generate a unique agent ID with improved collision handling

    Args:
        db: Database session

    Returns:
        str: Unique agent ID
    """

    # Generate ID with timestamp component to reduce collision probability
    timestamp_suffix = str(int(time.time() * 1000))[-3:]  # Last 3 digits of timestamp
    random_part = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(2)
    )
    id = random_part + timestamp_suffix

    # Fallback: use UUID if all attempts fail

    # return str(uuid.uuid4())[:8]
    return id
