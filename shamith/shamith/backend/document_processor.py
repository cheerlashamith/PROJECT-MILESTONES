"""
Document Processor – File Upload & Text Extraction
===================================================
Handles uploaded construction documents (PDF, TXT, images).
Extracts text content for AI analysis via Llama 3.1.
"""

import os
from typing import Optional
from backend.config import Config


class DocumentProcessor:
    """Processes uploaded documents for AI analysis."""

    SUPPORTED_TEXT_TYPES = [".pdf", ".txt", ".csv", ".md", ".docx"]
    SUPPORTED_IMAGE_TYPES = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
    MAX_TEXT_LENGTH = 8000  # chars to send to Llama

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def extract_text(self, uploaded_file) -> str:
        """
        Extract text content from an uploaded file.

        Args:
            uploaded_file: Streamlit UploadedFile object.

        Returns:
            Extracted text string, or error message.
        """
        filename = uploaded_file.name.lower()

        if filename.endswith(".pdf"):
            return self._extract_from_pdf(uploaded_file)
        elif filename.endswith(".txt") or filename.endswith(".md") or filename.endswith(".csv"):
            return self._extract_from_text(uploaded_file)
        elif filename.endswith(".docx"):
            return self._extract_from_docx(uploaded_file)
        elif any(filename.endswith(ext) for ext in self.SUPPORTED_IMAGE_TYPES):
            return self._describe_image(uploaded_file)
        else:
            return f"Unsupported file type: {os.path.splitext(filename)[1]}"

    def _extract_from_pdf(self, uploaded_file) -> str:
        """Extract text from a PDF file."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(uploaded_file)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i + 1} ---\n{page_text}")

            if text_parts:
                full_text = "\n\n".join(text_parts)
                # Truncate if too long
                if len(full_text) > self.MAX_TEXT_LENGTH:
                    full_text = full_text[:self.MAX_TEXT_LENGTH] + "\n\n[... truncated for AI processing]"
                return full_text
            else:
                return "Could not extract text from this PDF. It may be image-based (scanned document)."

        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def _extract_from_docx(self, uploaded_file) -> str:
        """Extract text from a Word document (.docx)."""
        try:
            from docx import Document
            
            doc = Document(uploaded_file)
            text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
            
            if text_parts:
                full_text = "\n".join(text_parts)
                if len(full_text) > self.MAX_TEXT_LENGTH:
                    full_text = full_text[:self.MAX_TEXT_LENGTH] + "\n\n[... truncated for AI processing]"
                return full_text
            else:
                return "Could not extract text from this DOCX. It may be empty."
        except ImportError:
            return "Error: python-docx library is not installed on the backend."
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    def _extract_from_text(self, uploaded_file) -> str:
        """Extract text from a plain text file."""
        try:
            content = uploaded_file.read().decode("utf-8", errors="replace")
            if len(content) > self.MAX_TEXT_LENGTH:
                content = content[:self.MAX_TEXT_LENGTH] + "\n\n[... truncated for AI processing]"
            return content
        except Exception as e:
            return f"Error reading text file: {str(e)}"

    def _describe_image(self, uploaded_file) -> str:
        """Return a description note for image files."""
        return (
            f"[Image uploaded: {uploaded_file.name}, "
            f"Size: {uploaded_file.size / 1024:.1f} KB]\n\n"
            f"Note: Llama 3.1 is a text-only model and cannot directly analyze images. "
            f"However, you can describe the image contents in the chat and I can provide "
            f"construction analysis based on your description."
        )

    def get_document_analysis_prompt(self, doc_text: str, filename: str) -> str:
        """
        Generate a prompt for AI to analyze a construction document.

        Args:
            doc_text: Extracted document text.
            filename: Original filename.

        Returns:
            Formatted prompt for Llama analysis.
        """
        return (
            f"I have uploaded a construction document named '{filename}'. "
            f"Please analyze its contents and provide:\n\n"
            f"1. A brief summary of what this document contains\n"
            f"2. Key project specifications mentioned\n"
            f"3. Materials or quantities referenced\n"
            f"4. Any important notes, dimensions, or requirements\n"
            f"5. How this relates to construction planning\n\n"
            f"Document contents:\n"
            f"{'=' * 40}\n"
            f"{doc_text}\n"
            f"{'=' * 40}"
        )

    def get_file_info(self, uploaded_file) -> dict:
        """Get basic file information."""
        return {
            "name": uploaded_file.name,
            "size_kb": round(uploaded_file.size / 1024, 1),
            "type": os.path.splitext(uploaded_file.name)[1].lower(),
        }
