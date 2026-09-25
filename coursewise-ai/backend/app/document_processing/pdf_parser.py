from pathlib import Path
from typing import List
from .base_parser import BaseDocumentParser, NormalizedDocument, NormalizedSection, DocumentParsingError
from ..services.pdf_service import PDFService, PDFProcessingError


class PDFParser(BaseDocumentParser):
    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"PDF file not found: {file_path}")

        try:
            pages, meta = PDFService.extract_text_and_structure(file_path)
        except PDFProcessingError as e:
            msg = str(e)
            if "insufficient or no extractable text" in msg.lower() or "scanned" in msg.lower():
                raise DocumentParsingError("This PDF appears to be scanned or image-based. Text extraction was unsuccessful.")
            raise DocumentParsingError(msg)
        except Exception as e:
            raise DocumentParsingError(f"Unable to extract readable text from this PDF: {str(e)}")

        sections: List[NormalizedSection] = []
        full_text_parts = []

        for idx, page in enumerate(pages):
            page_num = page["page_number"]
            cleaned_text = page["cleaned_text"]
            if not cleaned_text:
                continue

            full_text_parts.append(cleaned_text)

            # Detect main page heading if present
            blocks = page.get("blocks", [])
            heading = None
            for b in blocks:
                if b.get("is_heading"):
                    heading = b["text"].split("\n")[0][:100]
                    break

            sections.append(
                NormalizedSection(
                    section_index=idx,
                    content=cleaned_text,
                    source_type="pdf",
                    source_location=f"Page {page_num}",
                    heading=heading or f"Page {page_num}",
                    page_number=page_num,
                    section_name=f"Page {page_num}"
                )
            )

        total_pages = meta.get("total_pages", len(pages))
        doc_title = meta.get("title") or path.stem.replace("_", " ")

        return NormalizedDocument(
            filename=filename,
            file_type="pdf",
            mime_type="application/pdf",
            title=doc_title,
            total_units=total_pages,
            unit_label="pages",
            extracted_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata=meta
        )
