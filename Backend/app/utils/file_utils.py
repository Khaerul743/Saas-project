"""
File operations utilities for agent tasks
"""
import os
from typing import Dict, Optional, Tuple, List

from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_directory(user_id: int, agent_id: str) -> str:
    """
    Create directory for agent documents
    
    Args:
        user_id: ID of the user
        agent_id: ID of the agent
        
    Returns:
        str: Path to the created directory
    """
    directory_path = f"documents/user_{user_id}/agent_{agent_id}"
    if not os.path.exists(directory_path):
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
        
        # Determine content type based on file extension and MIME type
        filename = file_data["filename"].lower()
        mime_type = file_data.get("content_type", "").lower()
        
        if filename.endswith('.pdf') or mime_type == "application/pdf":
            content_type = "pdf"
        elif filename.endswith('.csv') or mime_type == "text/csv":
            content_type = "csv"
        elif filename.endswith(('.xlsx', '.xls')) or mime_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
            content_type = "excel"
        elif filename.endswith('.txt') or mime_type == "text/plain":
            content_type = "txt"
        else:
            # Default to txt for unknown types
            content_type = "txt"
        
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




#Customer Service Agent
from fastapi import UploadFile, HTTPException, status
from app.models.agent.customer_service_model import DatasetDescription
from app.utils.document_utils import write_document
from app.AI.utils import dataset

def get_filename_without_extension(filename: str) -> str:
    """Extract filename without extension"""
    return os.path.splitext(filename)[0]


def process_dataset_info(file_path: str, filename: str) -> str:
    """Process dataset and get info using get_dataset_info"""
    try:
        filename_without_ext = get_filename_without_extension(filename)
        return dataset.get_dataset_info(file_path, filename_without_ext)
    except Exception as e:
        logger.error(f"Error processing dataset info for {filename}: {str(e)}")
        return f"Error processing dataset {filename}: {str(e)}"


def get_content_type(file: UploadFile) -> str:
    filename = file.filename.lower()

    if file.content_type == "application/pdf" or filename.endswith('.pdf'):
        content_type = "pdf"
    elif file.content_type == "text/plain" or filename.endswith('.txt'):
        content_type = "txt"
    elif (file.content_type == "text/csv" or 
          file.content_type == "application/csv" or 
          filename.endswith('.csv')):
        content_type = "csv"
    elif (file.content_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ] or filename.endswith(('.xlsx', '.xls'))):
        content_type = "excel"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type must be pdf, txt, csv, or excel.",
        )
    return content_type

def process_file(files: List[UploadFile], directory_path: str, datasets: List[DatasetDescription]):
    available_databases = []
    dataset_descriptions = {}
    detail_data_parts = []
    for file in files:
        file_path = os.path.join(directory_path, file.filename)
        content_type = write_document(file, directory_path)
        if content_type in ["csv", "excel"]:

            filename_without_ext = get_filename_without_extension(file.filename)
            available_databases.append(filename_without_ext)

            dataset_desc = next((d for d in datasets if d.filename == filename_without_ext), None)
            if dataset_desc:
                dataset_descriptions[f"db_{filename_without_ext}_description"] = dataset_desc.description
            
            # Create database file in the same directory as documents
            db_path = os.path.join(directory_path, f"{filename_without_ext}.db")
            try:
                dataset.get_dataset(
                    file_path,
                    db_path,
                    f"SELECT * FROM {filename_without_ext}",
                    filename_without_ext,
                )
                logger.info(f"Created database {db_path} from {file.filename}")
            except Exception as e:
                logger.error(f"Failed to create database for {file.filename}: {str(e)}")
            
            # Get dataset info for detail_data
            try:
                dataset_info = process_dataset_info(file_path, file.filename)
                detail_data_parts.append(dataset_info)
                logger.info(f"Processed dataset info for {file.filename}")
            except Exception as e:
                logger.warning(f"Could not process dataset info for {file.filename}: {str(e)}")
                detail_data_parts.append(f"Dataset {file.filename}: Unable to process dataset information")
        
    return available_databases, dataset_descriptions, detail_data_parts

            