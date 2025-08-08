from typing import List, Dict, Any
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class PDFAnalyzer:
    """
    LLM-powered PDF content analyzer.
    
    Generates understanding, insights, and summaries from PDF documents
    using local Llama2 model through Ollama.
    """
    
    def __init__(self, ollama_model: str = "llama2", temperature: float = 0.3):
        """
        Initialize the PDF analyzer with local Llama2 model.
        
        Args:
            ollama_model: Name of the Ollama model to use
            temperature: LLM temperature (0.0-1.0, lower = more focused)
        """
        self.llm = self._initialize_ollama_model(ollama_model, temperature)
        self.analysis_prompt = self._create_analysis_prompt()
        self.summary_prompt = self._create_summary_prompt()
    
    def _initialize_ollama_model(self, model_name: str, temperature: float) -> Ollama:
        """
        Initialize and validate Ollama model connection.
        
        Args:
            model_name: Name of the Ollama model
            temperature: Model temperature setting
            
        Returns:
            Ollama: Initialized Ollama model instance
            
        Raises:
            Exception: If Ollama connection fails
        """
        try:
            llm = Ollama(model=model_name, temperature=temperature)
            logger.info(f"Using local model: {model_name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            logger.error("Make sure Ollama is installed and running:")
            logger.error("  1. Install: https://ollama.ai")
            logger.error("  2. Start: ollama serve")
            logger.error("  3. Pull model: ollama pull llama2")
            raise Exception(f"Ollama connection failed: {e}")
    
    def _robust_llm_call(self, prompt: str, max_retries: int = 2) -> str:
        """
        Make a robust LLM call with retry logic.
        
        Args:
            prompt: Prompt to send to LLM
            max_retries: Maximum number of retry attempts
            
        Returns:
            LLM response string
            
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"LLM call attempt {attempt + 1}/{max_retries + 1}")
                result = self.llm.invoke(prompt)
                if result and result.strip():
                    return result.strip()
                else:
                    logger.warning(f"Empty response from LLM on attempt {attempt + 1}")
                    if attempt == max_retries:
                        return "No meaningful response generated"
            except Exception as e:
                logger.error(f"LLM call failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries:
                    raise Exception(f"All LLM call attempts failed. Last error: {str(e)}")
                else:
                    logger.info(f"Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
        
        return "Failed to generate response"
    
    def _create_analysis_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for page-level analysis.
        
        Returns:
            PromptTemplate: Configured prompt template
        """
        return PromptTemplate(
            input_variables=["content", "page_info", "document_context"],
            template="""
                You are an expert document analyst. Analyze the following PDF content and provide comprehensive insights.

                Document Context: {document_context}
                Page Information: {page_info}

                Content to Analyze:
                {content}

                Please provide a detailed analysis including:

                1. **MAIN TOPICS & THEMES**
                - What are the primary subjects discussed?
                - What is the overall theme or purpose of this content?

                2. **KEY INFORMATION & INSIGHTS**
                - What are the most important facts, data, or findings?
                - Are there any notable statistics, dates, or figures?
                - What conclusions or recommendations are presented?

                3. **DOCUMENT STRUCTURE & TYPE**
                - What type of document is this (report, article, manual, etc.)?
                - How is the information organized?
                - Are there sections, headings, or clear divisions?

                4. **CONTENT QUALITY & CLARITY**
                - Is the writing clear and well-structured?
                - Are there any complex concepts that need explanation?
                - What is the target audience level?

                5. **ACTIONABLE TAKEAWAYS**
                - What are the key points someone should remember?
                - Are there any action items or next steps mentioned?
                - What value does this document provide to readers?

                Analysis:
                """
        )
    
    def _create_summary_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for document-level summarization.
        
        Returns:
            PromptTemplate: Configured prompt template
        """
        return PromptTemplate(
            input_variables=["full_content", "document_info"],
            template="""
                You are summarizing a complete PDF document. Create a comprehensive summary that captures the essence of the entire document.

                Document Information: {document_info}

                Full Document Content:
                {full_content}

                Please create a structured summary with:

                1. **EXECUTIVE SUMMARY** (2-3 sentences)
                - What is this document about in the simplest terms?

                2. **MAIN SECTIONS & CONTENT**
                - Break down the key sections and their main points
                - Include important data, findings, or arguments

                3. **KEY TAKEAWAYS**
                - List 5-7 most important points from the document
                - Focus on actionable insights and critical information

                4. **DOCUMENT CHARACTERISTICS**
                - Type: (Academic paper, business report, manual, etc.)
                - Complexity Level: (Beginner, Intermediate, Advanced)
                - Primary Purpose: (Inform, Persuade, Instruct, etc.)

                Summary:
                """
        )
    
    
    def analyze_single_page(self, document: Document) -> Dict[str, Any]:
        """
        Analyze a single page/document with LLM.
        
        Args:
            document: LangChain Document object to analyze
            
        Returns:
            Dict containing analysis results
        """
        page_number = document.metadata.get('page_number', 'unknown')
        logger.info(f"Analyzing page {page_number}")
        
        context_info = self._prepare_page_context(document)
        content = self._prepare_content_for_analysis(document.page_content)
        
        try:
            analysis_result = self._run_page_analysis(content, context_info)
            return self._format_page_analysis_result(document, analysis_result)
            
        except Exception as e:
            logger.error(f"Failed to analyze page {page_number}: {str(e)}")
            error_msg = f"Analysis failed: {str(e)}"
            if "broken pipe" in str(e).lower():
                error_msg = "Ollama service crashed. Please restart the application and try again."
            elif "connection" in str(e).lower():
                error_msg = "Cannot connect to Ollama. Please make sure Ollama is running."
            return self._format_error_result(document, error_msg)
    
    def _prepare_page_context(self, document: Document) -> Dict[str, str]:
        """
        Prepare context information for page analysis.
        
        Args:
            document: Document to analyze
            
        Returns:
            Dict containing page context information
        """
        return {
            "page_info": f"Page {document.metadata.get('page_number', 'N/A')} of {document.metadata.get('file_name', 'PDF')}",
            "document_context": f"File: {document.metadata.get('file_name', 'Unknown')}, Words: {document.metadata.get('word_count', 0)}"
        }
    
    def _prepare_content_for_analysis(self, content: str, max_length: int = 3000) -> str:
        """
        Prepare content for LLM analysis with length limits.
        
        Args:
            content: Original content
            max_length: Maximum content length
            
        Returns:
            Prepared content string
        """
        if len(content) <= max_length:
            return content
        return content[:max_length] + "\n\n[Content truncated for analysis...]"
    
    def _run_page_analysis(self, content: str, context_info: Dict[str, str]) -> str:
        """
        Run LLM analysis on page content.
        
        Args:
            content: Content to analyze
            context_info: Context information
            
        Returns:
            Analysis result string
            
        Raises:
            Exception: If LLM call fails
        """
        try:
            formatted_prompt = self.analysis_prompt.format(
                content=content,
                page_info=context_info["page_info"],
                document_context=context_info["document_context"]
            )
            return self._robust_llm_call(formatted_prompt)
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise Exception(f"Ollama call failed: {str(e)}")
    
    def _format_page_analysis_result(self, document: Document, analysis_result: str) -> Dict[str, Any]:
        """
        Format page analysis result.
        
        Args:
            document: Original document
            analysis_result: Analysis result string
            
        Returns:
            Formatted result dictionary
        """
        return {
            "page_number": document.metadata.get('page_number'),
            "analysis": analysis_result,
            "word_count": document.metadata.get('word_count', 0),
            "character_count": document.metadata.get('character_count', 0),
            "has_meaningful_content": document.metadata.get('word_count', 0) > 10
        }
    
    def _format_error_result(self, document: Document, error_message: str) -> Dict[str, Any]:
        """
        Format error result for failed analysis.
        
        Args:
            document: Original document
            error_message: Error message
            
        Returns:
            Error result dictionary
        """
        return {
            "page_number": document.metadata.get('page_number'),
            "analysis": f"Analysis failed: {error_message}",
            "error": True
        }
    
    def analyze_full_document(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Analyze the complete PDF document and generate comprehensive insights.
        
        Args:
            documents: List of Document objects (all pages)
            
        Returns:
            Dict containing complete document analysis
        """
        logger.info(f"Analyzing complete document with {len(documents)} pages")
        
        if not documents:
            return {"error": "No documents provided for analysis"}
        
        try:
            full_content = self._combine_document_content(documents)
            document_info = self._prepare_document_info(documents)
            summary_result = self._run_document_summary(full_content, document_info)
            
            return self._format_document_analysis_result(documents, summary_result)
            
        except Exception as e:
            logger.error(f"Failed to analyze full document: {str(e)}")
            error_msg = f"Document analysis failed: {str(e)}"
            if "broken pipe" in str(e).lower():
                error_msg = "Ollama service crashed during analysis. Please restart the application and try again."
            elif "connection" in str(e).lower():
                error_msg = "Cannot connect to Ollama. Please make sure Ollama is running."
            return self._format_document_error_result(documents, error_msg)
    
    def _combine_document_content(self, documents: List[Document], max_length: int = 8000) -> str:
        """
        Combine content from all documents with length limits.
        
        Args:
            documents: List of documents to combine
            max_length: Maximum content length
            
        Returns:
            Combined content string
        """
        full_content = ""
        for document in documents:
            if document.metadata.get('word_count', 0) > 0:
                page_content = document.page_content
                if len(full_content) + len(page_content) > max_length:
                    full_content += f"\n\n[Page {document.metadata.get('page_number')} content truncated...]"
                    break
                else:
                    full_content += f"\n\n--- Page {document.metadata.get('page_number')} ---\n{page_content}"
        
        return full_content
    
    def _prepare_document_info(self, documents: List[Document]) -> str:
        """
        Prepare document information for summary.
        
        Args:
            documents: List of documents
            
        Returns:
            Document information string
        """
        first_document = documents[0]
        total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)
        
        return (f"File: {first_document.metadata.get('file_name', 'PDF')}, "
                f"Pages: {len(documents)}, "
                f"Total Words: {total_words}")
    
    def _run_document_summary(self, full_content: str, document_info: str) -> str:
        """
        Run LLM summary on full document content.
        
        Args:
            full_content: Combined document content
            document_info: Document information
            
        Returns:
            Summary result string
            
        Raises:
            Exception: If LLM call fails
        """
        try:
            formatted_prompt = self.summary_prompt.format(
                full_content=full_content,
                document_info=document_info
            )
            return self._robust_llm_call(formatted_prompt)
        except Exception as e:
            logger.error(f"LLM summary failed: {str(e)}")
            raise Exception(f"Ollama call failed: {str(e)}")
    
    def _format_document_analysis_result(self, documents: List[Document], summary_result: str) -> Dict[str, Any]:
        """
        Format document analysis result.
        
        Args:
            documents: Original documents
            summary_result: Summary result string
            
        Returns:
            Formatted result dictionary
        """
        total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)
        first_document = documents[0]
        
        return {
            "document_summary": summary_result,
            "total_pages": len(documents),
            "total_words": total_words,
            "analysis_scope": "full_document",
            "file_name": first_document.metadata.get('file_name', 'Unknown')
        }
    
    def _format_document_error_result(self, documents: List[Document], error_message: str) -> Dict[str, Any]:
        """
        Format error result for failed document analysis.
        
        Args:
            documents: Original documents
            error_message: Error message
            
        Returns:
            Error result dictionary
        """
        total_words = sum(doc.metadata.get('word_count', 0) for doc in documents)
        
        return {
            "error": f"Document analysis failed: {error_message}",
            "total_pages": len(documents),
            "total_words": total_words
        }
    
    def generate_insights(self, documents: List[Document], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate insights from PDF documents based on analysis type.
        
        Args:
            documents: List of Document objects
            analysis_type: Type of analysis ("quick", "detailed", "comprehensive")
            
        Returns:
            Dict containing analysis results based on type
        """
        logger.info(f"Generating {analysis_type} insights for PDF")
        
        analysis_strategies = {
            "quick": self._perform_quick_analysis,
            "detailed": self._perform_detailed_analysis,
            "comprehensive": self._perform_comprehensive_analysis
        }
        
        strategy = analysis_strategies.get(analysis_type, self._perform_comprehensive_analysis)
        return strategy(documents)
    
    def _perform_quick_analysis(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Perform quick analysis on first few pages.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Quick analysis results
        """
        sample_documents = documents[:3]  # First 3 pages
        return self.analyze_full_document(sample_documents)
    
    def _perform_detailed_analysis(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Perform detailed analysis on individual pages.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Detailed analysis results
        """
        page_analyses = []
        max_pages = 5  # Limit to first 5 pages
        
        for document in documents[:max_pages]:
            if document.metadata.get('word_count', 0) > 0:
                analysis = self.analyze_single_page(document)
                page_analyses.append(analysis)
        
        overall_summary = self.analyze_full_document(documents)
        
        return {
            "analysis_type": "detailed",
            "page_analyses": page_analyses,
            "overall_summary": overall_summary,
            "pages_analyzed": len(page_analyses)
        }
    
    def _perform_comprehensive_analysis(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on full document.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Comprehensive analysis results
        """
        return {
            "analysis_type": "comprehensive",
            "document_summary": self.analyze_full_document(documents)
        }


def main():
    """Test the PDF analyzer functionality."""
    analyzer = PDFAnalyzer()
    print("PDF Analyzer initialized successfully!")
    print("Ready to analyze PDF documents with local Llama2 model.")


if __name__ == "__main__":
    main() 