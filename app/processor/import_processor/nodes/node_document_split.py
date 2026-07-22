import re
from typing import Tuple, List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState

REGEX_TITLE_LINE = r'^\s*#{1,6}\s+.+'
REGEX_CODE_BLOCK_MARKER = r'^(`{3,}|~{3,})'
NO_TITLE = "No Title"

class NodeDocumentSplit(BaseNode):

    name: str = "node_document_split"

    def _validate_input_state(self, state: ImportGraphState) -> Tuple[str, str]:
        file_title = state.get("file_title")
        if not file_title:
            raise StateFieldError(field_name="file_title", message="filename cannot be empty", expected_type=str)

        md_content = state.get("md_content")
        if not md_content:
            raise StateFieldError(field_name="md_content", message="file content cannot be empty", expected_type=str)

        md_content = md_content.replace("\r\n", "\n").replace("\r", "\n")

        return md_content, file_title

    def _split_by_headings(self, content: str, file_title: str) -> Tuple[List[Dict[str, str]], int, int]:
        def _flush_section():
            if not current_lines:
                return
            sections.append({
                "parent_title": _find_parent_title(current_title, sections),
                "title": current_title,
                "content": "\n".join(current_lines),
                "file_title": file_title,
            })
        
        def _find_parent_title(current_title: str, sections: List[Dict[str, str]]) -> str:
            current_level = _get_title_level(current_title)
            if current_level is None or current_level <= 1:
                return ""
            
            for section in reversed(sections):
                parent_title = section.get("title", "")
                parent_level = _get_title_level(parent_title)
                
                if parent_level is not None and parent_level < current_level:
                    return parent_title
            return ""

        def _get_title_level(title: str) -> Optional[int]:
            if not title:
                return None
            match = re.match(r'^(#{1,6})\s+', title)
            if not match:
                return None
            return len(match.group(1))


        sections = []
        title_count = 0
        current_title = ""
        current_lines = []
        in_code_block = False

        lines = content.split("\n")
        for line in lines:
            stripped_line = line.strip()

            code_block_marker_match = re.match(REGEX_CODE_BLOCK_MARKER, stripped_line)
            if code_block_marker_match:
                marker = code_block_marker_match.group(1)
                if not in_code_block:
                    in_code_block = True
                    code_block_start_marker = marker
                elif in_code_block and stripped_line == code_block_start_marker:
                    in_code_block = False
                    code_block_start_marker = None
                current_lines.append(line)
                continue

            is_valid_title = (not in_code_block) and re.match(REGEX_TITLE_LINE, line)
            if is_valid_title:
                _flush_section()
                current_title = stripped_line
                current_lines = [current_title]
                title_count += 1
                self.logger.info(f"Found heading line: {current_title}")
            else:
                # non-heading line
                current_lines.append(line)

        _flush_section()
        self.logger.info(f"Document split by headings completed, total {len(sections)} sections, title count: {title_count}, total lines: {len(lines)}")
        return sections, title_count, len(lines)

    def _no_headings_fallback(self, content: str, sections: List[Dict[str, str]], title_count: int, file_title: str) -> List[Dict[str, str]]:
        if title_count == 0:
            self.logger.warning(f"No headings detected, process as a single section: {file_title}")
            return [{"title": NO_TITLE, "content": content, "file_title": file_title}]
        return sections

    def _split_and_merge(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
        splitted = []
        for sec in sections:
            splitted.extend(self._split_overlong_chunk(sec))
        self.logger.info(f"Step 4-1: overlong sections further splitted into {len(splitted)} chunks")

        merged = self._merge_tiny_chunks(splitted)
        self.logger.info(f"Step 4-2: tiny chunks merged into {len(merged)} chunks")
        return merged

    def _split_overlong_chunk(self, section: Dict[str, str]) -> List[Dict[str, str]]:

        content = section.get("content", "")
        if len(content) <= self.config.max_content_length:
            return [section]

        title = section.get("title", "")
        prefix = f"{title}\n\n" if title else ""
        available_len = self.config.max_content_length - len(prefix)
        if available_len <= 0:
            self.logger.info(f"Long section title, cannot be further splitted: {title[:20]}...")
            return [section]

        # remove duplicate title
        body = content
        if title and body.lstrip().startswith(title):
            body = body[body.find(title) + len(title):].lstrip()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=available_len,
            chunk_overlap=0,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],
        )

        splitted = []
        chunks = splitter.split_text(body)
        for idx, chunk in enumerate(chunks, start=1):
            text = chunk.strip()
            if not text:
                continue

            full_text = (prefix + text).strip()
            splitted.append({
                "title": f"{title}-{idx}" if title else f"chunk-{idx}",
                "content": full_text,
                "parent_title": title,
                "part": idx,
                "file_title": section.get("file_title"),
            })

        self.logger.debug(f"Overlong section ({title}) splitted into {len(splitted)} chunks")
        return splitted

    def _merge_tiny_chunks(self, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not chunks:
            self.logger.info("No sections to merge")
            return []

        merged = []
        to_merge = None 
        merge_count = 1

        for chunk in chunks:
            if to_merge is None:
                to_merge = chunk
                continue

            is_current_short = len(to_merge["content"]) < self.config.min_content_length
            is_same_parent = to_merge.get("parent_title") == chunk.get("parent_title")
            self.logger.debug(f'Checking merge condition: prev {to_merge.get("parent_title")}, current {chunk.get("parent_title")}, can merge: {is_same_parent}')

            if is_current_short and is_same_parent:
                # remove duplicate parent title from next content before merge
                parent_title = chunk.get("parent_title", "")
                next_content = chunk["content"]
                if parent_title and next_content.startswith(parent_title):
                    next_content = next_content[len(parent_title):].lstrip()
                # merge content, space-separated
                to_merge["content"] += "\n\n" + next_content
                merge_count += 1
                # update sub-chunk part
                if "part" in chunk:
                    to_merge["part"] = chunk["part"]
                self.logger.debug(f"merged tiny chunk: {to_merge.get('parent_title') or to_merge.get('title')} -> accumulated length {len(to_merge['content'])}, merged {merge_count} chunks")
            else:
                # reset merge cursor if merge condition not satisfied
                merged.append(to_merge)
                to_merge = chunk
                merge_count = 1

        # append the last chunk
        if to_merge is not None:
            merged.append(to_merge)

        self.logger.debug(f"Tiny chunks merged {len(chunks)} -> {len(merged)}")
        return merged

    def process(self, state: ImportGraphState) -> ImportGraphState:

        content, file_title = self._validate_input_state(state)

        sections, title_count, lines_count = self._split_by_headings(content, file_title)

        sections = self._no_headings_fallback(content, sections, title_count, file_title)

        sections = self._split_and_merge(sections)

        self.logger.info("-" * 50 + " chunking stats " + "-" * 50)
        self.logger.info(f"MD file line count: {lines_count}")
        self.logger.info(f"Final chunks count: {len(sections)}")
        self.backup_json(state, sections, "chunks.json")

        return { "chunks": sections }