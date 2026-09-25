from .document_normalizer import DocumentNormalizer, SUPPORTED_EXTENSIONS
from .base_parser import NormalizedDocument, NormalizedSection, DocumentParsingError

def parse_document(file_path: str, filename: str) -> NormalizedDocument:
    return DocumentNormalizer.parse_document(file_path, filename)
