from fastapi import UploadFile
from fastapi import HTTPException, status
import os
import shutil


def write_document(file: UploadFile, directory_path: str):
    if file.content_type == "application/pdf":
        content_type = "pdf"
    elif file.content_type == "application/txt":
        content_type = "txt"
    else:
        content_type = "docs"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type must be pdf or txt.",
        )
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return content_type