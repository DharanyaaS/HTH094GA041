import re
from typing import List, Dict, Any

# Regex to match numbered sections like:
# "1. Purpose", "2. Data Access", "Section 3. Data Sharing", "Article 4 - Data Retention"
SECTION_HEADER_PATTERN = re.compile(
    r'(?:^|\n)\s*(?:(?:Section|Article|Clause)\s+)?(\d+(?:\.\d+)*\.?\s+[A-Za-z][^\n]{1,80})',
    re.IGNORECASE
)

def chunk_policy_pages(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split extracted policy pages into smart section-based chunks.
    Each section retains:
    - chunk_id
    - title
    - text (section heading + content)
    - page (source page number)
    - source (source filename)
    """
    chunks: List[Dict[str, Any]] = []
    chunk_index = 1

    for page_info in pages_data:
        page_num = page_info["page"]
        raw_text = page_info["text"]
        source_name = page_info["source"]

        if not raw_text.strip():
            continue

        # Look for section matches within this page
        matches = list(SECTION_HEADER_PATTERN.finditer(raw_text))

        if matches:
            # Process sections within this page
            for i, match in enumerate(matches):
                title = match.group(1).strip()
                start_pos = match.start()
                end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
                section_body = raw_text[start_pos:end_pos].strip()

                if section_body:
                    clean_source = re.sub(r'[^a-zA-Z0-9_-]', '_', source_name)
                    chunk_id = f"{clean_source}_p{page_num}_s{chunk_index}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "title": title,
                        "text": section_body,
                        "page": page_num,
                        "source": source_name
                    })
                    chunk_index += 1
        else:
            # Fallback for pages without standard numbered sections:
            # Split by double newlines (paragraphs)
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [raw_text.strip()]

            for p_idx, para in enumerate(paragraphs):
                # First line as tentative title
                lines = para.split("\n")
                para_title = lines[0][:60].strip() if lines else f"Page {page_num} Section {p_idx+1}"
                clean_source = re.sub(r'[^a-zA-Z0-9_-]', '_', source_name)
                chunk_id = f"{clean_source}_p{page_num}_p{p_idx+1}_{chunk_index}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "title": para_title,
                    "text": para,
                    "page": page_num,
                    "source": source_name
                })
                chunk_index += 1

    return chunks
