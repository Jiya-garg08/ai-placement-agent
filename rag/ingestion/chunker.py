import re
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Union

from schemas.rag_schema import KnowledgeChunk


class MarkdownDocumentChunker:
    """Recursive markdown chunker preserving header hierarchy, section context, and metadata."""

    def __init__(self, target_chunk_size: int = 800, chunk_overlap: int = 120):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (approximately 4 characters per token for English text)."""
        return max(1, len(text) // 4)

    def chunk_markdown_text(self, text: str, source_filename: str) -> List[KnowledgeChunk]:
        """Parse markdown text into structured, hierarchical KnowledgeChunks."""
        chunks: List[KnowledgeChunk] = []
        
        # 1. Extract Main Document Title (first '# Title')
        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else Path(source_filename).stem.replace("_", " ").title()

        # Remove top level title from text
        clean_text = re.sub(r'^#\s+.+$', '', text, count=1, flags=re.MULTILINE).strip()

        # 2. Split into major sections by '## Section'
        section_splits = re.split(r'\n(?=##\s+)', clean_text)
        chunk_idx = 0

        for sec in section_splits:
            if not sec.strip():
                continue
            
            # Check section heading
            sec_header_match = re.match(r'^##\s+(.+)$', sec.strip(), re.MULTILINE)
            if not sec_header_match and not sec.strip().startswith("##"):
                # Preamble without a ## heading; only keep if it has substantial content
                if len(sec.strip()) < 30:
                    continue
                sec_name = "Overview"
                body = sec.strip()
            else:
                sec_name = sec_header_match.group(1).strip() if sec_header_match else "Overview"
                body = re.sub(r'^##\s+.+$', '', sec.strip(), flags=re.MULTILINE).strip()

            if not body:
                continue

            # Split large body by paragraphs if exceeds target size
            if len(body) <= self.target_chunk_size:
                c_text = f"## {sec_name}\n\n{body}"
                chunk_id = f"{Path(source_filename).stem}-{sec_name.lower().replace(' ', '_')[:20]}-{chunk_idx}"
                chunks.append(KnowledgeChunk(
                    id=chunk_id,
                    title=doc_title,
                    topic=doc_title,
                    subtopic=sec_name,
                    section=sec_name,
                    content=c_text,
                    token_count=self.estimate_tokens(c_text),
                    source_file=source_filename
                ))
                chunk_idx += 1
            else:
                # Sub-split into overlapping chunks
                paragraphs = body.split("\n\n")
                buffer = ""
                for p in paragraphs:
                    if len(buffer) + len(p) > self.target_chunk_size and buffer:
                        c_text = f"## {sec_name}\n\n{buffer.strip()}"
                        chunk_id = f"{Path(source_filename).stem}-{sec_name.lower().replace(' ', '_')[:20]}-{chunk_idx}"
                        chunks.append(KnowledgeChunk(
                            id=chunk_id,
                            title=doc_title,
                            topic=doc_title,
                            subtopic=sec_name,
                            section=sec_name,
                            content=c_text,
                            token_count=self.estimate_tokens(c_text),
                            source_file=source_filename
                        ))
                        chunk_idx += 1
                        # Retain overlap from end of buffer
                        buffer = buffer[-self.chunk_overlap:] + "\n\n" + p
                    else:
                        buffer = (buffer + "\n\n" + p).strip()

                if buffer.strip():
                    c_text = f"## {sec_name}\n\n{buffer.strip()}"
                    chunk_id = f"{Path(source_filename).stem}-{sec_name.lower().replace(' ', '_')[:20]}-{chunk_idx}"
                    chunks.append(KnowledgeChunk(
                        id=chunk_id,
                        title=doc_title,
                        topic=doc_title,
                        subtopic=sec_name,
                        section=sec_name,
                        content=c_text,
                        token_count=self.estimate_tokens(c_text),
                        source_file=source_filename
                    ))
                    chunk_idx += 1

        return chunks

    def chunk_directory(self, dir_path: Union[str, Path]) -> List[KnowledgeChunk]:
        """Traverse a directory and chunk all markdown files."""
        all_chunks: List[KnowledgeChunk] = []
        path = Path(dir_path)
        for md_file in sorted(path.glob("*.md")):
            with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            doc_chunks = self.chunk_markdown_text(content, md_file.name)
            all_chunks.extend(doc_chunks)
        return all_chunks
