from pathlib import Path
from typing import List
from .base_parser import BaseDocumentParser, NormalizedDocument, NormalizedSection, DocumentParsingError


class TXTParser(BaseDocumentParser):
    ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    def parse(self, file_path: str, filename: str) -> NormalizedDocument:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"Text file not found: {file_path}")

        raw_content = None
        used_encoding = None

        for enc in self.ENCODINGS:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    raw_content = f.read()
                used_encoding = enc
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if raw_content is None:
            raise DocumentParsingError("Unable to decode text file. Ensure it is encoded in UTF-8 or standard ASCII.")

        lines = raw_content.splitlines()
        if not any(line.strip() for line in lines):
            raise DocumentParsingError("This text file appears to be empty.")

        sections: List[NormalizedSection] = []
        doc_title = None

        # Look for title in first non-empty line
        for line in lines[:5]:
            stripped = line.strip()
            if stripped:
                doc_title = stripped[:80]
                break

        # Group lines into logical chunks (~25 to 50 lines per section)
        LINE_CHUNK_SIZE = 35
        current_chunk_lines: List[str] = []
        start_line_num = 1
        section_idx = 0

        for idx, line in enumerate(lines, start=1):
            current_chunk_lines.append(line)
            # Break chunk on paragraph gap if threshold reached, or at max size
            if len(current_chunk_lines) >= LINE_CHUNK_SIZE and (not line.strip() or len(current_chunk_lines) >= LINE_CHUNK_SIZE + 15):
                chunk_text = "\n".join(current_chunk_lines).strip()
                if chunk_text:
                    end_line_num = idx
                    sections.append(
                        NormalizedSection(
                            section_index=section_idx,
                            content=chunk_text,
                            source_type="txt",
                            source_location=f"Lines {start_line_num}-{end_line_num}",
                            heading=f"Lines {start_line_num}-{end_line_num}",
                            section_name=f"Lines {start_line_num}-{end_line_num}",
                            start_line=start_line_num,
                            end_line=end_line_num,
                            metadata={"encoding": used_encoding}
                        )
                    )
                    section_idx += 1
                current_chunk_lines = []
                start_line_num = idx + 1

        # Flush remaining lines
        if current_chunk_lines:
            chunk_text = "\n".join(current_chunk_lines).strip()
            if chunk_text:
                end_line_num = len(lines)
                sections.append(
                    NormalizedSection(
                        section_index=section_idx,
                        content=chunk_text,
                        source_type="txt",
                        source_location=f"Lines {start_line_num}-{end_line_num}",
                        heading=f"Lines {start_line_num}-{end_line_num}",
                        section_name=f"Lines {start_line_num}-{end_line_num}",
                        start_line=start_line_num,
                        end_line=end_line_num,
                        metadata={"encoding": used_encoding}
                    )
                )

        if not sections:
            raise DocumentParsingError("This text file contains no readable text content.")

        return NormalizedDocument(
            filename=filename,
            file_type="txt",
            mime_type="text/plain",
            title=doc_title or path.stem.replace("_", " "),
            total_units=len(lines),
            unit_label="lines",
            extracted_text=raw_content.strip(),
            sections=sections,
            metadata={"encoding": used_encoding, "line_count": len(lines)}
        )
