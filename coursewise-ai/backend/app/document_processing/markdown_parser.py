import re
from pathlib import Path
from typing import List
from .base_parser import BaseDocumentParser, NormalizedDocument, NormalizedSection, DocumentParsingError


class MarkdownParser(BaseDocumentParser):
    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"Markdown file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                raw_text = f.read()
        except Exception as e:
            raise DocumentParsingError(f"Failed to read Markdown file: {str(e)}")

        lines = raw_text.splitlines()
        if not any(l.strip() for l in lines):
            raise DocumentParsingError("This Markdown file appears to be empty.")

        sections: List[NormalizedSection] = []
        doc_title = None
        current_heading = "Introduction"
        current_lines: List[str] = []
        section_idx = 0

        def flush():
            nonlocal section_idx, current_lines
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append(
                        NormalizedSection(
                            section_index=section_idx,
                            content=body,
                            source_type="md",
                            source_location=f"Section: {current_heading}",
                            heading=current_heading,
                            section_name=current_heading
                        )
                    )
                    section_idx += 1
                current_lines = []

        for line in lines:
            # Check for Markdown heading (# Heading)
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if heading_match:
                title_text = heading_match.group(2).strip()
                if not doc_title and len(heading_match.group(1)) == 1:
                    doc_title = title_text
                flush()
                current_heading = title_text
            else:
                current_lines.append(line)

        flush()

        if not sections:
            raise DocumentParsingError("This Markdown file contains no readable text content.")

        return NormalizedDocument(
            filename=filename,
            file_type="md",
            mime_type="text/markdown",
            title=doc_title or path.stem.replace("_", " "),
            total_units=len(sections),
            unit_label="sections",
            extracted_text=raw_text.strip(),
            sections=sections,
            metadata={"section_count": len(sections)}
        )
