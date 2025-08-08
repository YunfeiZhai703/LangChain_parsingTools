"""
File handling utilities for PDF upload and processing.
"""

import os
import shutil
import tempfile
from typing import Tuple
from fastapi import UploadFile, HTTPException
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


def validate_uploaded_file(file: UploadFile) -> None:
    """
    Validate uploaded file for size and type.
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If file validation fails
    """
    _validate_file_size(file)
    _validate_file_type(file)


def _validate_file_size(file: UploadFile) -> None:
    """
    Validate file size against configured limits.
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If file is too large
    """
    if file.size and file.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB"
        )


def _validate_file_type(file: UploadFile) -> None:
    """
    Validate file type against allowed extensions.
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If file type is not supported
    """
    file_extension = os.path.splitext(file.filename.lower())[1]
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )


def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file to temporary location.
    
    Args:
        file: Uploaded file object
        
    Returns:
        str: Path to saved file
        
    Raises:
        HTTPException: If file saving fails
    """
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1],
            dir=settings.UPLOAD_DIR
        )
        
        # Write file content
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        logger.info(f"File saved temporarily: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file"
        )


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file after processing.
    
    Args:
        file_path: Path to temporary file
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")


def get_file_info(file: UploadFile) -> dict:
    """
    Get information about uploaded file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: File information
    """
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "size_mb": round(file.size / (1024 * 1024), 2) if file.size else 0
    } 