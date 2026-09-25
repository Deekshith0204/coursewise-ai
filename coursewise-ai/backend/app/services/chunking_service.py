import re
import uuid
from typing import List, Dict, Any, Optional
from ..document_processing.base_parser import NormalizedDocument, NormalizedSection


class ChunkingService:
    TARGET_WORDS = 350
    MAX_WORDS = 650
    MIN_WORDS = 25

    @classmethod
    def create_chunks_from_normalized(
        cls,
        document_id: str,
        normalized_doc: NormalizedDocument
    ) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from a NormalizedDocument preserving the
        file-specific source locations (Page N, Slide N, Section X, Lines Y-Z).
        """
        chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for section in normalized_doc.sections:
            text = section.content.strip()
            if not text:
                continue

            words = text.split()
            # If section fits within MAX_WORDS, create single chunk directly
            if len(words) <= cls.MAX_WORDS:
                chunks.append(cls._build_unified_chunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    heading=section.heading,
                    text=text,
                    source_type=section.source_type,
                    source_location=section.source_location,
                    page_number=section.page_number,
                    slide_number=section.slide_number,
                    section_name=section.section_name,
                    start_line=section.start_line,
                    end_line=section.end_line
                ))
                chunk_index += 1
            else:
                # Split large section into sub-chunks along paragraphs and sentences
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                curr_words: List[str] = []
                curr_parts: List[str] = []

                for para in paragraphs:
                    p_words = para.split()
                    if len(curr_words) + len(p_words) <= cls.MAX_WORDS:
                        curr_words.extend(p_words)
                        curr_parts.append(para)
                    else:
                        if len(p_words) > cls.MAX_WORDS:
                            sentences = cls._split_into_sentences(para)
                            for s in sentences:
                                s_words = s.split()
                                if len(curr_words) + len(s_words) > cls.MAX_WORDS and len(curr_words) >= cls.MIN_WORDS:
                                    sub_text = "\n\n".join(curr_parts).strip()
                                    chunks.append(cls._build_unified_chunk(
                                        document_id=document_id,
                                        chunk_index=chunk_index,
                                        heading=section.heading,
                                        text=sub_text,
                                        source_type=section.source_type,
                                        source_location=section.source_location,
                                        page_number=section.page_number,
                                        slide_number=section.slide_number,
                                        section_name=section.section_name,
                                        start_line=section.start_line,
                                        end_line=section.end_line
                                    ))
                                    chunk_index += 1
                                    curr_words = []
                                    curr_parts = []
                                curr_words.extend(s_words)
                                curr_parts.append(s)
                        else:
                            if curr_parts:
                                sub_text = "\n\n".join(curr_parts).strip()
                                chunks.append(cls._build_unified_chunk(
                                    document_id=document_id,
                                    chunk_index=chunk_index,
                                    heading=section.heading,
                                    text=sub_text,
                                    source_type=section.source_type,
                                    source_location=section.source_location,
                                    page_number=section.page_number,
                                    slide_number=section.slide_number,
                                    section_name=section.section_name,
                                    start_line=section.start_line,
                                    end_line=section.end_line
                                ))
                                chunk_index += 1
                            curr_words = list(p_words)
                            curr_parts = [para]

                if curr_parts:
                    sub_text = "\n\n".join(curr_parts).strip()
                    if sub_text:
                        chunks.append(cls._build_unified_chunk(
                            document_id=document_id,
                            chunk_index=chunk_index,
                            heading=section.heading,
                            text=sub_text,
                            source_type=section.source_type,
                            source_location=section.source_location,
                            page_number=section.page_number,
                            slide_number=section.slide_number,
                            section_name=section.section_name,
                            start_line=section.start_line,
                            end_line=section.end_line
                        ))
                        chunk_index += 1

        return chunks

    @classmethod
    def create_chunks(
        cls,
        document_id: str,
        cleaned_pages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Legacy/compatibility method for raw cleaned_pages list.
        """
        chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for page in cleaned_pages:
            page_num = page["page_number"]
            page_text = page["cleaned_text"]
            if not page_text:
                continue

            raw_paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            current_heading: Optional[str] = None
            current_chunk_words: List[str] = []
            current_chunk_text_parts: List[str] = []

            for paragraph in raw_paragraphs:
                is_heading = cls._is_heading(paragraph)
                if is_heading:
                    if len(current_chunk_words) >= cls.MIN_WORDS:
                        chunk_text = "\n\n".join(current_chunk_text_parts).strip()
                        chunks.append(cls._build_unified_chunk(
                            document_id=document_id,
                            chunk_index=chunk_index,
                            heading=current_heading,
                            text=chunk_text,
                            source_type="pdf",
                            source_location=f"Page {page_num}",
                            page_number=page_num
                        ))
                        chunk_index += 1
                        current_chunk_words = []
                        current_chunk_text_parts = []
                    current_heading = paragraph.split("\n")[0][:120]
                    if len(paragraph.split()) <= 10:
                        continue

                para_words = paragraph.split()
                if len(current_chunk_words) + len(para_words) <= cls.MAX_WORDS:
                    current_chunk_words.extend(para_words)
                    current_chunk_text_parts.append(paragraph)
                else:
                    if len(para_words) > cls.MAX_WORDS:
                        sentences = cls._split_into_sentences(paragraph)
                        for sent in sentences:
                            sent_words = sent.split()
                            if len(current_chunk_words) + len(sent_words) > cls.MAX_WORDS and len(current_chunk_words) >= cls.MIN_WORDS:
                                chunk_text = "\n\n".join(current_chunk_text_parts).strip()
                                chunks.append(cls._build_unified_chunk(
                                    document_id=document_id,
                                    chunk_index=chunk_index,
                                    heading=current_heading,
                                    text=chunk_text,
                                    source_type="pdf",
                                    source_location=f"Page {page_num}",
                                    page_number=page_num
                                ))
                                chunk_index += 1
                                current_chunk_words = []
                                current_chunk_text_parts = []
                            current_chunk_words.extend(sent_words)
                            current_chunk_text_parts.append(sent)
                    else:
                        chunk_text = "\n\n".join(current_chunk_text_parts).strip()
                        chunks.append(cls._build_unified_chunk(
                            document_id=document_id,
                            chunk_index=chunk_index,
                            heading=current_heading,
                            text=chunk_text,
                            source_type="pdf",
                            source_location=f"Page {page_num}",
                            page_number=page_num
                        ))
                        chunk_index += 1
                        current_chunk_words = list(para_words)
                        current_chunk_text_parts = [paragraph]

            if current_chunk_text_parts:
                chunk_text = "\n\n".join(current_chunk_text_parts).strip()
                if chunk_text:
                    chunks.append(cls._build_unified_chunk(
                        document_id=document_id,
                        chunk_index=chunk_index,
                        heading=current_heading,
                        text=chunk_text,
                        source_type="pdf",
                        source_location=f"Page {page_num}",
                        page_number=page_num
                    ))
                    chunk_index += 1

        return chunks

    @staticmethod
    def _is_heading(text: str) -> bool:
        first_line = text.strip().split("\n")[0]
        if len(first_line) > 100:
            return False
        if re.match(r"^(\d+(\.\d+)*|[A-Z](\.\d+)*)\s+[A-Za-z]", first_line):
            return True
        if re.match(r"^(Chapter|Section|Module|Part|Slide)\s+\d+", first_line, re.IGNORECASE):
            return True
        if first_line.isupper() and 3 < len(first_line) < 60:
            return True
        return False

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def _build_unified_chunk(
        document_id: str,
        chunk_index: int,
        heading: Optional[str],
        text: str,
        source_type: str = "pdf",
        source_location: str = "Page 1",
        page_number: Optional[int] = None,
        slide_number: Optional[int] = None,
        section_name: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        words = text.split()
        token_count = int(len(words) * 1.3)
        return {
            "id": str(uuid.uuid4()),
            "document_id": document_id,
            "chunk_index": chunk_index,
            "heading": heading or source_location,
            "text": text,
            "source_type": source_type,
            "source_location": source_location,
            "page_number": page_number,
            "slide_number": slide_number,
            "section_name": section_name or heading,
            "start_line": start_line,
            "end_line": end_line,
            "token_count": token_count,
            "embedding": None
        }
