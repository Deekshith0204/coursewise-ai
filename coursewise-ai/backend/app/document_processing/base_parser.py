from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


class DocumentParsingError(Exception):
    """Raised when parsing or extracting content from a document fails."""
    pass


@dataclass
class NormalizedSection:
    section_index: int
    content: str
    source_type: str  # 'pdf', 'docx', 'pptx', 'txt', 'md'
    source_location: str  # e.g., 'Page 4', 'Slide 7', 'Section: Introduction', 'Lines 20-45'
    heading: Optional[str] = None
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_name: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedDocument:
    filename: str
    file_type: str  # 'pdf', 'docx', 'pptx', 'txt', 'md'
    mime_type: str
    title: str
    total_units: int  # pages, slides, sections, or lines
    unit_label: str  # 'pages', 'slides', 'sections', 'lines'
    extracted_text: str
    sections: List[NormalizedSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        """Parse file and return a unified NormalizedDocument."""
        pass
