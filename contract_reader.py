import re
from typing import List, Dict, Any

# Matches numbered clauses e.g., "1. Data Access", "Section 2: Data Sharing", "Clause 3 - ..."
CLAUSE_HEADER_PATTERN = re.compile(
    r'(?:^|\n)\s*(?:(?:Section|Clause|Article)\s+)?(\d+(?:\.\d+)*\.?\s+[A-Za-z][^\n]{1,80})',
    re.IGNORECASE
)

def extract_clauses_from_text(raw_text: str, filename: str = "contract.txt") -> List[Dict[str, Any]]:
    """
    Automatically extracts individual contract clauses from text.
    Returns a list of structured clauses:
    [
        {
            "clause_id": "Clause 1",
            "title": "Data Access",
            "full_clause": "1. Data Access\nEmployees may access customer data...",
            "body": "Employees may access customer data...",
            "source": "contract.txt"
        },
        ...
    ]
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Contract content is empty.")

    clean_text = raw_text.replace("\r\n", "\n").strip()
    matches = list(CLAUSE_HEADER_PATTERN.finditer(clean_text))
    clauses: List[Dict[str, Any]] = []

    if matches:
        for i, match in enumerate(matches):
            header_line = match.group(1).strip()
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
            
            section_content = clean_text[start_pos:end_pos].strip()
            # Separate the header line and the body
            lines = section_content.split("\n", 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            # Extract clause numbering if available
            number_match = re.search(r'(\d+(?:\.\d+)*)', title)
            clause_num = number_match.group(1) if number_match else str(i + 1)
            
            # Clean title (remove number prefix for clean display)
            clean_title = re.sub(r'^(?:(?:Section|Clause|Article)\s+)?\d+(?:\.\d+)*\.?\s*', '', title).strip()
            if not clean_title:
                clean_title = title

            clauses.append({
                "clause_id": f"Clause {clause_num}",
                "title": clean_title,
                "full_clause": section_content,
                "body": body,
                "source": filename
            })
    else:
        # Fallback: Split by double newlines if no standard numbering found
        blocks = [b.strip() for b in clean_text.split("\n\n") if b.strip()]
        for idx, block in enumerate(blocks, start=1):
            lines = block.split("\n", 1)
            first_line = lines[0].strip()
            remaining = lines[1].strip() if len(lines) > 1 else first_line
            clauses.append({
                "clause_id": f"Clause {idx}",
                "title": first_line[:50],
                "full_clause": block,
                "body": remaining,
                "source": filename
            })

    if not clauses:
        raise ValueError("Could not extract any valid clauses from contract.")

    return clauses
