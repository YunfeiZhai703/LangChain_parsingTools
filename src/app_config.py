"""
FastAPI application configuration and initialization.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from src.document_loader import MultiFormatDocumentLoader
from src.llm_analyzer import PDFAnalyzer

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="PDF Parser with LangChain",
        description="Upload PDFs and get intelligent analysis using LangChain and Llama2",
        version="1.0.0"
    )
    
    _configure_middleware(app)
    _configure_startup_event(app)
    
    return app


def _configure_middleware(app: FastAPI) -> None:
    """
    Configure middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _configure_startup_event(app: FastAPI) -> None:
    """
    Configure startup event for application initialization.
    
    Args:
        app: FastAPI application instance
    """
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application on startup."""
        logger.info("Starting PDF Parser application...")
        
        try:
            _validate_configuration()
            _initialize_components()
            _log_startup_info()
            
        except Exception as e:
            logger.error(f"Startup failed: {str(e)}")
            raise e


def _validate_configuration() -> None:
    """Validate application configuration."""
    settings.validate()
    logger.info("Configuration validated successfully")


def _initialize_components() -> None:
    """Initialize application components if not already initialized."""
    global document_loader, pdf_analyzer
    
    # Only initialize if not already done
    if document_loader is None or pdf_analyzer is None:
        try:
            settings.validate()
            document_loader = MultiFormatDocumentLoader()
            pdf_analyzer = PDFAnalyzer(ollama_model=settings.OLLAMA_MODEL)
            logger.info("Document processing components initialized")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise e
    else:
        logger.info("Document processing components already initialized")


def _log_startup_info() -> None:
    """Log startup information."""
    logger.info(f"Using local Llama2 model: {settings.OLLAMA_MODEL}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Max file size: {settings.MAX_FILE_SIZE_MB}MB")


# Global instances (initialized immediately)
try:
    settings.validate()
    document_loader = MultiFormatDocumentLoader()
    pdf_analyzer = PDFAnalyzer(ollama_model=settings.OLLAMA_MODEL)
    logger.info("Document processing components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    document_loader = None
    pdf_analyzer = None 