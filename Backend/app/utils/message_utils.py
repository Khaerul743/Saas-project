"""
Utility functions for handling message length and validation.
"""

from typing import Optional


def truncate_message(message: str, max_length: int = 10000) -> str:
    """
    Truncate message if it exceeds max_length.
    
    Args:
        message: The message to potentially truncate
        max_length: Maximum allowed length (default: 10000)
    
    Returns:
        Truncated message with ellipsis if needed
    """
    if not message:
        return message
    
    if len(message) <= max_length:
        return message
    
    # Truncate and add ellipsis
    truncated = message[:max_length-3] + "..."
    return truncated


def validate_message_length(message: str, max_length: int = 10000) -> tuple[bool, Optional[str]]:
    """
    Validate if message length is within acceptable limits.
    
    Args:
        message: The message to validate
        max_length: Maximum allowed length (default: 10000)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return True, None
    
    if len(message) > max_length:
        return False, f"Message too long. Maximum length is {max_length} characters, got {len(message)}"
    
    return True, None


def safe_message_length(message: str, max_length: int = 10000) -> str:
    """
    Safely handle message length by truncating if necessary.
    This is the recommended function to use when saving messages.
    
    Args:
        message: The message to process
        max_length: Maximum allowed length (default: 10000)
    
    Returns:
        Safe message that fits within length limits
    """
    if not message:
        return message
    
    return truncate_message(message, max_length)
