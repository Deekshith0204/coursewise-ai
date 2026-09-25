import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import docx
from .base_parser import BaseDocumentParser, NormalizedDocument, NormalizedSection, DocumentParsingError


class DOCXParser(BaseDocumentParser):
    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"Word document not found: {file_path}")

        try:
            doc = docx.Document(file_path)
        except Exception as e:
            raise DocumentParsingError(f"Failed to open Word document: {str(e)}")

        sections: List[NormalizedSection] = []
        doc_title: Optional[str] = None
        current_section_name: str = "Introduction"
        current_paragraphs: List[str] = []
        section_index = 0

        # Helper to flush accumulated paragraphs into a NormalizedSection
        def flush_section():
            nonlocal section_index, current_paragraphs
            if current_paragraphs:
                content = "\n\n".join(current_paragraphs).strip()
                if content:
                    sections.append(
                        NormalizedSection(
                            section_index=section_index,
                            content=content,
                            source_type="docx",
                            source_location=f"Section: {current_section_name}",
                            heading=current_section_name,
                            section_name=current_section_name,
                            metadata={"paragraph_count": len(current_paragraphs)}
                        )
                    )
                    section_index += 1
                current_paragraphs = []

        # Iterate through body elements (paragraphs and tables)
        for element in doc.element.body:
            tag = element.tag
            if tag.endswith('p'):
                # Paragraph
                p = docx.text.paragraph.Paragraph(element, doc)
                text = p.text.strip()
                if not text:
                    continue

                style_name = p.style.name.lower() if p.style and p.style.name else ""

                # Check if it's a document title
                if "title" in style_name and not doc_title:
                    doc_title = text
                    continue

                # Check if it's a heading
                if "heading" in style_name or re.match(r"^(\d+(\.\d+)*)\s+[A-Z]", text):
                    flush_section()
                    current_section_name = text[:100]
                else:
                    # Normal paragraph or list item
                    if "list" in style_name or p.style.name.startswith("List"):
                        current_paragraphs.append(f"• {text}")
                    else:
                        current_paragraphs.append(text)

            elif tag.endswith('tbl'):
                # Table
                table = docx.table.Table(element, doc)
                table_lines = []
                for row_idx, row in enumerate(table.rows):
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    # Filter duplicate merged cell text across adjacent columns
                    cleaned_cells = []
                    for c_idx, cell_text in enumerate(row_cells):
                        if c_idx > 0 and cell_text == row_cells[c_idx - 1] and cell_text != "":
                            continue
                        cleaned_cells.append(cell_text)
                    if cleaned_cells and any(cleaned_cells):
                        table_lines.append("| " + " | ".join(cleaned_cells) + " |")

                if table_lines:
                    # Insert separator line after header row if more than 1 row
                    if len(table_lines) > 1:
                        col_count = len(table.columns)
                        sep = "| " + " | ".join(["---"] * col_count) + " |"
                        table_lines.insert(1, sep)
                    current_paragraphs.append("Table Data:\n" + "\n".join(table_lines))

        # Flush final section
        flush_section()

        if not sections:
            raise DocumentParsingError("This Word document appears to be empty or contains no readable text.")

        if not doc_title:
            doc_title = sections[0].heading if sections else path.stem.replace("_", " ")

        full_text = "\n\n".join(s.content for s in sections)

        return NormalizedDocument(
            filename=filename,
            file_type="docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            title=doc_title or path.stem.replace("_", " "),
            total_units=len(sections),
            unit_label="sections",
            extracted_text=full_text,
            sections=sections,
            metadata={"section_count": len(sections)}
        )
