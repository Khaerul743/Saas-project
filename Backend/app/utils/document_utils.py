from fastapi import UploadFile
from fastapi import HTTPException, status
import os
import shutil


def write_document(file: UploadFile, directory_path: str):
    """
    Write uploaded file to directory and return content type.
    
    Args:
        file: Uploaded file
        directory_path: Directory to save the file
        
    Returns:
        str: Content type of the file
        
    Raises:
        HTTPException: If file type is not supported
    """
    # Determine content type based on file extension and MIME type
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
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    
    # Write file to disk
    file_path = os.path.join(directory_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return content_type