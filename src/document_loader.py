"""
Multi-format document loader with LangChain integration.

Handles PDF, image, XLS, and CSV file parsing, text extraction, and metadata collection.
Provides enhanced document objects with rich metadata for analysis.
"""

import os
import csv
import io
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

# Additional processing libraries
import pandas as pd
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class MultiFormatDocumentLoader:
    """
    Advanced multi-format document loader with LangChain integration.
    
    Handles PDF, image, XLS, and CSV parsing, text extraction, and metadata collection.
    Provides enhanced document objects with rich metadata for analysis.
    """
    
    def __init__(self):
        """Initialize the document loader with supported file extensions."""
        self.supported_extensions = {
            '.pdf',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            # Spreadsheets
            '.xls', '.xlsx', '.xlsm',
            # CSV
            '.csv'
        }
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file exists and is a supported file type.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.supported_extensions:
            logger.error(f"Unsupported file type: {file_extension}")
            return False
        
        return True
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load and process a document based on its file type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List[Document]: List of Document objects with extracted content and metadata
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid file: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        logger.info(f"Loading {file_extension} file: {file_path}")
        
        try:
            if file_extension == '.pdf':
                return self._load_pdf(file_path)
            elif file_extension in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
                return self._load_image(file_path)
            elif file_extension in {'.xls', '.xlsx', '.xlsm'}:
                return self._load_excel(file_path)
            elif file_extension == '.csv':
                return self._load_csv(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading {file_extension} file: {str(e)}")
            raise
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF using PyPDFLoader."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Enhance metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    'file_type': 'pdf',
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'page_number': i + 1,
                    'total_pages': len(documents),
                    'word_count': len(doc.page_content.split()),
                    'char_count': len(doc.page_content)
                })
            
            logger.info(f"Successfully loaded PDF with {len(documents)} pages")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            raise
    
    def _load_image(self, file_path: str) -> List[Document]:
        """Load image and extract text using OCR."""
        try:
            # Open and process image
            image = Image.open(file_path)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            if not extracted_text.strip():
                extracted_text = "[Image contains no readable text or requires manual analysis]"
            
            # Create document
            document = Document(
                page_content=extracted_text,
                metadata={
                    'file_type': 'image',
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'page_number': 1,
                    'total_pages': 1,
                    'word_count': len(extracted_text.split()),
                    'char_count': len(extracted_text),
                    'image_format': image.format,
                    'image_size': image.size,
                    'image_mode': image.mode
                }
            )
            
            logger.info(f"Successfully loaded image with OCR text extraction")
            return [document]
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise
    
    def _load_excel(self, file_path: str) -> List[Document]:
        """Load Excel file and convert to text format."""
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            documents = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to readable text
                content_lines = [f"Sheet: {sheet_name}", ""]
                
                # Add column headers
                content_lines.append("Columns: " + ", ".join(df.columns.astype(str)))
                content_lines.append("")
                
                # Add data rows (limit to prevent huge content)
                max_rows = min(100, len(df))  # Limit to 100 rows
                for i in range(max_rows):
                    row_data = []
                    for col in df.columns:
                        value = df.iloc[i][col]
                        if pd.isna(value):
                            row_data.append("")
                        else:
                            row_data.append(str(value))
                    content_lines.append(" | ".join(row_data))
                
                if len(df) > max_rows:
                    content_lines.append(f"... and {len(df) - max_rows} more rows")
                
                page_content = "\n".join(content_lines)
                
                # Create document for each sheet
                document = Document(
                    page_content=page_content,
                    metadata={
                        'file_type': 'excel',
                        'file_name': os.path.basename(file_path),
                        'file_path': file_path,
                        'sheet_name': sheet_name,
                        'page_number': len(documents) + 1,
                        'total_pages': len(excel_file.sheet_names),
                        'word_count': len(page_content.split()),
                        'char_count': len(page_content),
                        'rows_count': len(df),
                        'columns_count': len(df.columns),
                        'columns': list(df.columns.astype(str))
                    }
                )
                documents.append(document)
            
            logger.info(f"Successfully loaded Excel file with {len(documents)} sheets")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise
    
    def _load_csv(self, file_path: str) -> List[Document]:
        """Load CSV file and convert to text format."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to readable text
            content_lines = []
            
            # Add column headers
            content_lines.append("Columns: " + ", ".join(df.columns.astype(str)))
            content_lines.append("")
            
            # Add data rows (limit to prevent huge content)
            max_rows = min(100, len(df))  # Limit to 100 rows
            for i in range(max_rows):
                row_data = []
                for col in df.columns:
                    value = df.iloc[i][col]
                    if pd.isna(value):
                        row_data.append("")
                    else:
                        row_data.append(str(value))
                content_lines.append(" | ".join(row_data))
            
            if len(df) > max_rows:
                content_lines.append(f"... and {len(df) - max_rows} more rows")
            
            page_content = "\n".join(content_lines)
            
            # Create document
            document = Document(
                page_content=page_content,
                metadata={
                    'file_type': 'csv',
                    'file_name': os.path.basename(file_path),
                    'file_path': file_path,
                    'page_number': 1,
                    'total_pages': 1,
                    'word_count': len(page_content.split()),
                    'char_count': len(page_content),
                    'rows_count': len(df),
                    'columns_count': len(df.columns),
                    'columns': list(df.columns.astype(str))
                }
            )
            
            logger.info(f"Successfully loaded CSV file with {len(df)} rows")
            return [document]
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise
    
    def get_document_summary(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Generate a summary of the loaded documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Dict containing document summary information
        """
        if not documents:
            return {"error": "No documents provided"}
        
        first_doc = documents[0]
        file_type = first_doc.metadata.get('file_type', 'unknown')
        
        summary = {
            "file_name": first_doc.metadata.get('file_name', 'Unknown'),
            "file_type": file_type,
            "total_pages": len(documents),
            "total_words": sum(doc.metadata.get('word_count', 0) for doc in documents),
            "total_characters": sum(doc.metadata.get('char_count', 0) for doc in documents)
        }
        
        # Add file-type specific information
        if file_type == 'excel':
            summary["sheets"] = [doc.metadata.get('sheet_name') for doc in documents]
        elif file_type == 'csv':
            summary["rows"] = first_doc.metadata.get('rows_count', 0)
            summary["columns"] = first_doc.metadata.get('columns_count', 0)
        elif file_type == 'image':
            summary["image_format"] = first_doc.metadata.get('image_format')
            summary["image_size"] = first_doc.metadata.get('image_size')
        
        return summary


def main():
    """Test the document loader functionality."""
    loader = MultiFormatDocumentLoader()
    print("Multi-format Document Loader initialized successfully!")
    print("Supported file types:", loader.supported_extensions)


if __name__ == "__main__":
    main()