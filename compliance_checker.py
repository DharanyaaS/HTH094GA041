from typing import List, Dict, Any
from .contract_reader import extract_clauses_from_text
from .embedding import generate_embedding
from .vector_store import query_policy_store, count_chunks
from .conflict_detector import analyze_clause_conflict

DEFAULT_SIMILARITY_THRESHOLD = 0.55

def check_contract_compliance(
    contract_text: str,
    contract_filename: str = "contract.txt",
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> Dict[str, Any]:
    """
    Complete compliance analysis workflow:
    1. Automatically extracts clauses from the contract text.
    2. Embeds each clause and retrieves top policy evidence from ChromaDB.
    3. Evaluates relevance threshold: if below threshold, marks as 'Not Found'.
    4. Runs conflict detection to identify policy conflicts and risk level.
    5. Returns structured compliance report with metrics.
    """
    clauses = extract_clauses_from_text(contract_text, contract_filename)
    total_chunks = count_chunks()

    findings: List[Dict[str, Any]] = []

    # Counters for report summary
    total_clauses = len(clauses)
    conflicts_count = 0
    compliant_count = 0
    not_found_count = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    unknown_risk_count = 0

    for clause in clauses:
        if total_chunks == 0:
            # No policies uploaded / indexed at all
            finding = analyze_clause_conflict(
                clause=clause,
                retrieved_chunk=None,
                similarity_score=0.0,
                threshold=threshold
            )
        else:
            # Query embedding for clause
            # We embed both the title and body for rich semantic context
            query_str = f"{clause.get('title', '')}: {clause.get('body', '')}".strip()
            if not query_str:
                query_str = clause.get('full_clause', '')
                
            query_emb = generate_embedding(query_str)
            candidates = query_policy_store(query_emb, n_results=3)

            top_chunk = candidates[0] if candidates else None
            top_similarity = top_chunk["similarity"] if top_chunk else 0.0

            # Special verification for unmatched domains:
            # If the top similarity is below threshold or topical overlap is absent
            finding = analyze_clause_conflict(
                clause=clause,
                retrieved_chunk=top_chunk,
                similarity_score=top_similarity,
                threshold=threshold
            )

        # Update stats
        status = finding.get("status")
        risk = finding.get("risk")

        if status == "Conflict":
            conflicts_count += 1
        elif status == "Compliant":
            compliant_count += 1
        else:
            not_found_count += 1

        if risk == "High":
            high_risk_count += 1
        elif risk == "Medium":
            medium_risk_count += 1
        elif risk == "Low":
            low_risk_count += 1
        else:
            unknown_risk_count += 1

        findings.append(finding)

    return {
        "summary": {
            "total_clauses": total_clauses,
            "conflicts": conflicts_count,
            "compliant": compliant_count,
            "not_found": not_found_count,
            "high_risk": high_risk_count,
            "medium_risk": medium_risk_count,
            "low_risk": low_risk_count,
            "unknown_risk": unknown_risk_count,
            "indexed_policy_chunks": total_chunks
        },
        "findings": findings,
        "disclaimer": "This tool provides document-based compliance assistance and does not replace professional legal advice."
    }
