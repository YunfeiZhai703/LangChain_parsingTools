"""
Configuration settings for the PDF parsing application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Configuration settings for the PDF parsing application."""
    
    # Model Configuration
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    # Supported file types
    ALLOWED_EXTENSIONS = {
        ".pdf",
        # Images
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
        # Spreadsheets
        ".xls", ".xlsx", ".xlsm",
        # CSV
        ".csv"
    }
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required settings are present.
        
        Returns:
            bool: True if validation passes
        """
        cls._ensure_upload_directory()
        return True
    
    @classmethod
    def _ensure_upload_directory(cls) -> None:
        """Ensure upload directory exists."""
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)


# Global settings instance
settings = Settings() 