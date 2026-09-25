import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import pymupdf  # PyMuPDF


class PDFProcessingError(Exception):
    pass


class PDFService:
    @staticmethod
    def extract_text_and_structure(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract text, headings, and structure from a PDF file preserving page numbers.
        Returns:
            pages: List of dicts with page_number, raw_text, cleaned_text, blocks
            metadata: Dict with title, total_pages, total_chars
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFProcessingError(f"PDF file not found at: {file_path}")

        try:
            doc = pymupdf.open(file_path)
        except Exception as e:
            raise PDFProcessingError(f"Failed to open PDF: {str(e)}")

        if len(doc) == 0:
            doc.close()
            raise PDFProcessingError("PDF is empty (0 pages).")

        raw_pages: List[Dict[str, Any]] = []
        doc_title = doc.metadata.get("title", "").strip() or path.stem

        total_extracted_chars = 0
        header_candidates: Dict[str, int] = {}
        footer_candidates: Dict[str, int] = {}

        # First pass: extract text and collect potential running headers/footers
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)

            text_blocks: List[Dict[str, Any]] = []
            page_text_lines = []

            for b in blocks:
                # block_type 0 is text
                if len(b) >= 5 and b[6] == 0:
                    b_text = b[4].strip()
                    if b_text:
                        text_blocks.append({
                            "bbox": (b[0], b[1], b[2], b[3]),
                            "text": b_text,
                            "is_heading": PDFService._is_heading_candidate(b_text, b)
                        })
                        page_text_lines.append(b_text)

            combined_page_text = "\n".join(page_text_lines)
            total_extracted_chars += len(combined_page_text)

            # Record first and last non-empty lines for recurring header/footer detection
            if page_text_lines:
                first_line = page_text_lines[0].strip()
                last_line = page_text_lines[-1].strip()
                if len(first_line) < 80:
                    header_candidates[first_line] = header_candidates.get(first_line, 0) + 1
                if len(last_line) < 80:
                    footer_candidates[last_line] = footer_candidates.get(last_line, 0) + 1

            raw_pages.append({
                "page_number": page_num,
                "raw_text": combined_page_text,
                "blocks": text_blocks
            })

        doc.close()

        # Check if PDF is scanned or has no extractable text
        if total_extracted_chars < 50:
            raise PDFProcessingError(
                "PDF contains insufficient or no extractable text. "
                "It may be a scanned image or protected document."
            )

        # Identify repeating headers/footers occurring across at least 40% of pages (min 2)
        min_threshold = max(2, int(len(raw_pages) * 0.4))
        repeated_headers = {h for h, count in header_candidates.items() if count >= min_threshold}
        repeated_footers = {f for f, count in footer_candidates.items() if count >= min_threshold}

        # Second pass: clean text while preserving headings and meaningful content
        cleaned_pages: List[Dict[str, Any]] = []
        for p in raw_pages:
            cleaned_text = PDFService._clean_page_text(
                p["raw_text"],
                repeated_headers,
                repeated_footers
            )

            cleaned_pages.append({
                "page_number": p["page_number"],
                "raw_text": p["raw_text"],
                "cleaned_text": cleaned_text,
                "blocks": p["blocks"]
            })

        metadata = {
            "title": doc_title,
            "total_pages": len(cleaned_pages),
            "total_chars": total_extracted_chars
        }

        return cleaned_pages, metadata

    @staticmethod
    def _is_heading_candidate(text: str, block: Tuple) -> bool:
        """Heuristic to detect if a block is likely a section heading."""
        lines = text.strip().split("\n")
        if len(lines) > 2:
            return False
        first_line = lines[0].strip()
        if len(first_line) > 100:
            return False
        # Heading patterns: "1. Introduction", "Chapter 2", "1.1 Background", all caps, or title case
        if re.match(r"^(\d+(\.\d+)*|[A-Z](\.\d+)*)\s+[A-Z]", first_line):
            return True
        if re.match(r"^(Chapter|Section|Module|Unit|Part)\s+\d+", first_line, re.IGNORECASE):
            return True
        if first_line.isupper() and 3 < len(first_line) < 60:
            return True
        return False

    @staticmethod
    def _clean_page_text(text: str, headers_to_remove: set, footers_to_remove: set) -> str:
        """Remove recurring headers/footers, fix line wraps and whitespace."""
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Filter recurring headers/footers
            if stripped in headers_to_remove or stripped in footers_to_remove:
                continue
            # Filter isolated page numbers like "12" or "- 12 -"
            if re.match(r"^[-–—\s]*\d+[-–—\s]*$", stripped):
                continue
            cleaned_lines.append(stripped)

        raw_joined = "\n".join(cleaned_lines)

        # Fix hyphenated line breaks: e.g. "distri-\nbuted" -> "distributed"
        dehyphenated = re.sub(r"(\w+)-\n(\w+)", r"\1\2", raw_joined)

        # Normalize multiple blank lines to double newline for paragraphs
        normalized = re.sub(r"\n{3,}", "\n\n", dehyphenated)

        # Normalize spaces
        cleaned = re.sub(r"[ \t]+", " ", normalized)

        return cleaned.strip()
