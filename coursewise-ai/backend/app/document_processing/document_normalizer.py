import os
from pathlib import Path
from typing import Dict, Type
from .base_parser import BaseDocumentParser, NormalizedDocument, DocumentParsingError
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .pptx_parser import PPTXParser
from .txt_parser import TXTParser
from .markdown_parser import MarkdownParser

PARSER_REGISTRY: Dict[str, Type[BaseDocumentParser]] = {
    ".pdf": PDFParser,
    ".docx": DOCXParser,
    ".pptx": PPTXParser,
    ".txt": TXTParser,
    ".md": MarkdownParser,
}

SUPPORTED_EXTENSIONS = set(PARSER_REGISTRY.keys())

MIME_TYPE_MAPPING = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".md": "text/markdown",
}


class DocumentNormalizer:
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Extract normalized file extension in lowercase."""
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise DocumentParsingError(
                f"Unsupported file type '{ext}'. Please upload PDF, DOCX, PPTX, or TXT."
            )
        return ext.lstrip(".")

    @staticmethod
    def get_mime_type(filename: str) -> str:
        ext = Path(filename).suffix.lower()
        return MIME_TYPE_MAPPING.get(ext, "application/octet-stream")

    @classmethod
    def parse_document(cls, file_path: str, filename: str) -> NormalizedDocument:
        """
        Detect file type, select the corresponding parser,
        and return a unified NormalizedDocument.
        """
        ext = Path(filename).suffix.lower()
        parser_cls = PARSER_REGISTRY.get(ext)
        if not parser_cls:
            raise DocumentParsingError(
                f"Unsupported file type '{ext}'. Please upload PDF, DOCX, PPTX, or TXT."
            )

        parser = parser_cls()
        normalized_doc = parser.parse(file_path=file_path, filename=filename)
        return normalized_doc
