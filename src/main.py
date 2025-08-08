"""
Main FastAPI application for PDF parsing with LangChain.
"""

import sys
import os
from typing import Dict, Any
from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app_config import create_app, document_loader, pdf_analyzer
from src.file_handlers import validate_uploaded_file, save_uploaded_file, cleanup_temp_file, get_file_info

logger = logging.getLogger(__name__)

# Create FastAPI application
app = create_app()


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "CybParser API",
        "description": "AI-powered PDF analysis API with LangChain and Llama2",
        "version": "1.0.0",
        "endpoints": {
            "analyze_pdf": "POST /api/analyze-pdf/",
            "health": "GET /api/health",
            "api_info": "GET /api/info"
        },
        "frontend": "React frontend available at http://localhost:3000"
    }



@app.post("/api/analyze-pdf/")
async def analyze_pdf(
    file: UploadFile = File(...),
    analysis_type: str = Form("comprehensive")
):
    """
    Main endpoint for PDF analysis.
    
    Args:
        file: Uploaded PDF file
        analysis_type: Type of analysis ("quick", "detailed", "comprehensive")
        
    Returns:
        JSON response with analysis results
    """
    logger.info(f"Received PDF upload: {file.filename} ({file.size} bytes)")
    
    temp_file_path = None
    try:
        # Validate and save file
        validate_uploaded_file(file)
        temp_file_path = save_uploaded_file(file)
        
            # Process Document
    if document_loader is None:
        raise Exception("Document loader not initialized. Please restart the application.")

    documents = document_loader.load_document(temp_file_path)
    document_summary = document_loader.get_document_summary(documents)
        
        logger.info(f"Loaded document: {len(documents)} pages/sections")
        
        # Analyze with LLM
        if pdf_analyzer is None:
            raise Exception("PDF analyzer not initialized. Please restart the application.")
        
        analysis_result = pdf_analyzer.generate_insights(documents, analysis_type)
        
        logger.info(f"Analysis completed: {analysis_type}")
        
        # Return results
        return JSONResponse(content={
            "success": True,
            "document_summary": document_summary,
            "analysis": analysis_result,
            "analysis_type": analysis_type,
            "file_info": get_file_info(file)
        })
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing failed: {str(e)}"}
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "document_loader": "ready" if document_loader else "not initialized",
        "pdf_analyzer": "ready" if pdf_analyzer else "not initialized"
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "app_name": "CybParser API",
        "version": "1.0.0",
        "description": "AI-powered PDF analysis API with LangChain and Llama2",
        "supported_formats": ["PDF", "Images (JPG, PNG, etc.)", "Excel (XLS, XLSX)", "CSV"],
        "analysis_types": ["detailed", "comprehensive"],
        "endpoints": {
            "analyze_pdf": "POST /api/analyze-pdf/",
            "health": "GET /api/health",
            "api_info": "GET /api/info"
        },
        "features": [
            "PDF text extraction",
            "LangChain integration", 
            "Local Llama2 analysis",
            "Multiple analysis types",
            "Rich metadata extraction",
            "API-only backend"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 