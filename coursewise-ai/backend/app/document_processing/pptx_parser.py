from pathlib import Path
from typing import List, Optional
from pptx import Presentation
from .base_parser import BaseDocumentParser, NormalizedDocument, NormalizedSection, DocumentParsingError


class PPTXParser(BaseDocumentParser):
    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"PowerPoint file not found: {file_path}")

        try:
            prs = Presentation(file_path)
        except Exception as e:
            raise DocumentParsingError(f"This PowerPoint file could not be processed: {str(e)}")

        if len(prs.slides) == 0:
            raise DocumentParsingError("This PowerPoint file contains no slides.")

        sections: List[NormalizedSection] = []
        doc_title: Optional[str] = None
        full_text_parts: List[str] = []

        for slide_idx, slide in enumerate(prs.slides):
            slide_number = slide_idx + 1
            slide_title = None
            slide_content_lines: List[str] = []

            # 1. Slide Title
            if slide.shapes.title and slide.shapes.title.text.strip():
                slide_title = slide.shapes.title.text.strip()
                if not doc_title and slide_number == 1:
                    doc_title = slide_title

            # 2. Iterate through shapes (text boxes, bullet points, tables)
            for shape in slide.shapes:
                if shape == slide.shapes.title:
                    continue  # already captured

                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        text = para.text.strip()
                        if not text:
                            continue
                        # If paragraph has level > 0 or bullet formatting
                        if para.level > 0:
                            slide_content_lines.append(f"{'  ' * para.level}• {text}")
                        else:
                            slide_content_lines.append(f"• {text}" if len(text) < 120 else text)

                elif shape.has_table:
                    table = shape.table
                    table_rows = []
                    for row in table.rows:
                        cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                        if any(cells):
                            table_rows.append("| " + " | ".join(cells) + " |")
                    if table_rows:
                        if len(table_rows) > 1:
                            col_count = len(table.columns)
                            sep = "| " + " | ".join(["---"] * col_count) + " |"
                            table_rows.insert(1, sep)
                        slide_content_lines.append("Table:\n" + "\n".join(table_rows))

            # 3. Speaker notes
            notes_text = ""
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                raw_notes = slide.notes_slide.notes_text_frame.text.strip()
                if raw_notes:
                    notes_text = f"\n[Speaker Notes]: {raw_notes}"

            # Assemble slide section
            heading = slide_title or f"Slide {slide_number}"
            body_text = "\n".join(slide_content_lines).strip()
            total_slide_text = f"{heading}\n\n{body_text}{notes_text}".strip()

            if total_slide_text:
                full_text_parts.append(total_slide_text)
                sections.append(
                    NormalizedSection(
                        section_index=slide_idx,
                        content=total_slide_text,
                        source_type="pptx",
                        source_location=f"Slide {slide_number}",
                        heading=heading,
                        slide_number=slide_number,
                        section_name=heading,
                        metadata={
                            "slide_number": slide_number,
                            "has_notes": bool(notes_text)
                        }
                    )
                )

        if not sections:
            raise DocumentParsingError("This PowerPoint file appears to be empty or contains no readable text.")

        return NormalizedDocument(
            filename=filename,
            file_type="pptx",
            mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            title=doc_title or path.stem.replace("_", " "),
            total_units=len(prs.slides),
            unit_label="slides",
            extracted_text="\n\n".join(full_text_parts),
            sections=sections,
            metadata={"slide_count": len(prs.slides)}
        )
