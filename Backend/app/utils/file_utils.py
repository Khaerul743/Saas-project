"""
File operations utilities for agent tasks
"""
import os
from typing import Dict, Optional, Tuple

from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_directory(user_id: int, agent_id: int) -> str:
    """
    Create directory for agent documents
    
    Args:
        user_id: ID of the user
        agent_id: ID of the agent
        
    Returns:
        str: Path to the created directory
    """
    directory_path = f"documents/user_{user_id}/agent_{agent_id}"
    os.makedirs(directory_path, exist_ok=True)
    logger.info(f"Created directory: {directory_path}")
    return directory_path


def save_uploaded_file(file_data: Dict, directory_path: str) -> Tuple[str, str]:
    """
    Save uploaded file to directory
    
    Args:
        file_data: File data dictionary containing filename, content, content_type
        directory_path: Directory to save the file
        
    Returns:
        Tuple[str, str]: (file_path, content_type)
        
    Raises:
        Exception: If file saving fails
    """
    try:
        # Create file path
        file_path = os.path.join(directory_path, file_data["filename"])
        
        # Write file content from hex string
        file_content = bytes.fromhex(file_data["content"])
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Determine content type
        content_type = (
            "pdf" if file_data["content_type"] == "application/pdf" else "txt"
        )
        
        logger.info(f"Saved file: {file_path} (type: {content_type})")
        return file_path, content_type
        
    except Exception as e:
        logger.error(f"Failed to save file {file_data.get('filename', 'unknown')}: {e}")
        raise e


def cleanup_file_on_error(file_path: str) -> None:
    """
    Remove file if it exists (for rollback purposes)
    
    Args:
        file_path: Path to the file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Rollback: Removed file {file_path}")
    except Exception as e:
        logger.error(f"Failed to remove file {file_path} during rollback: {e}")
