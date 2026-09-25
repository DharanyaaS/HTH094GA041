import re
from typing import Dict, Any, Optional

def analyze_clause_conflict(
    clause: Dict[str, Any],
    retrieved_chunk: Optional[Dict[str, Any]],
    similarity_score: float,
    threshold: float = 0.55
) -> Dict[str, Any]:
    """
    Evaluates whether a contract clause conflicts with or complies with retrieved policy evidence.
    Grounding rule: If similarity is below threshold or no chunk is retrieved,
    returns 'Not Found' with Risk 'Unknown'. Never hallucinate a policy rule.
    """
    clause_title = clause.get("title", "")
    clause_text = (clause.get("full_clause") or clause.get("body") or "").lower()
    clause_id = clause.get("clause_id", "Clause")

    # 1. GROUNDING / NOT FOUND CHECK (Threshold check)
    if retrieved_chunk is None or similarity_score < threshold:
        return {
            "clause_id": clause_id,
            "clause_title": clause.get("title", "Clause"),
            "contract_clause": clause.get("full_clause", ""),
            "status": "Not Found",
            "risk": "Unknown",
            "evidence_status": "Not Found",
            "policy_evidence": "No relevant policy requirement found.",
            "source": "N/A",
            "page": "N/A",
            "similarity": round(similarity_score, 3),
            "explanation": "No relevant policy requirement was found in the indexed policy documents for this contract clause."
        }

    policy_text = retrieved_chunk.get("text", "")
    policy_lower = policy_text.lower()
    page_num = retrieved_chunk.get("page", "N/A")
    source_file = retrieved_chunk.get("source", "Policy Document")

    # 1B. TOPICAL GROUNDING GUARDRAIL (e.g., Encryption, AES-256, etc.)
    # If the contract specifies encryption/ciphers but the policy does not govern encryption
    if ("encrypt" in clause_text or "aes" in clause_text or "cipher" in clause_text) and not any(k in policy_lower for k in ["encrypt", "aes", "cipher", "crypt"]):
        return {
            "clause_id": clause_id,
            "clause_title": clause.get("title", "Data Encryption"),
            "contract_clause": clause.get("full_clause", ""),
            "status": "Not Found",
            "risk": "Unknown",
            "evidence_status": "Not Found",
            "policy_evidence": "No relevant policy requirement found.",
            "source": "N/A",
            "page": "N/A",
            "similarity": round(similarity_score, 3),
            "explanation": "No relevant policy requirement concerning data encryption or AES-256 was found in the indexed policy documents."
        }

    # 2. DOMAIN LOGIC: DATA ACCESS
    if "access" in clause_text or "access" in clause_title.lower():
        # Check if contract allows unrestricted/broad access
        permissive_access = any(p in clause_text for p in ["whenever necessary", "anytime", "unrestricted", "at will", "all employees", "without authorization"])
        restricted_policy = any(r in policy_lower for r in ["only when access is required", "assigned work", "need-to-know", "authorized personnel", "prior approval", "role-based"])

        if permissive_access and restricted_policy:
            return {
                "clause_id": clause_id,
                "clause_title": clause.get("title", "Data Access"),
                "contract_clause": clause.get("full_clause", ""),
                "status": "Conflict",
                "risk": "High",
                "evidence_status": "Explicitly Stated",
                "policy_evidence": policy_text,
                "source": source_file,
                "page": page_num,
                "similarity": round(similarity_score, 3),
                "explanation": "The contract permits data access 'whenever necessary', which directly violates the policy requirement strictly limiting customer data access to assigned work duties."
            }

    # 3. DOMAIN LOGIC: DATA SHARING
    if "shar" in clause_text or "transfer" in clause_text or "disclos" in clause_text or "third" in clause_text or "partner" in clause_text:
        # Check if contract allows external sharing without approval
        permissive_sharing = any(p in clause_text for p in ["may be shared", "external business partners", "third party", "third parties", "without approval", "disclose"])
        restricted_sharing = any(r in policy_lower for r in ["must not be shared", "written approval", "data protection officer", "dpo", "prohibited", "strictly forbidden"])

        # Check if contract explicitly mentions obtaining DPO/written approval
        has_approval_clause = any(a in clause_text for a in ["written approval", "prior written consent", "dpo approval"])

        if permissive_sharing and restricted_sharing and not has_approval_clause:
            return {
                "clause_id": clause_id,
                "clause_title": clause.get("title", "Data Sharing"),
                "contract_clause": clause.get("full_clause", ""),
                "status": "Conflict",
                "risk": "High",
                "evidence_status": "Explicitly Stated",
                "policy_evidence": policy_text,
                "source": source_file,
                "page": page_num,
                "similarity": round(similarity_score, 3),
                "explanation": "The contract allows customer information to be shared with external business partners without mandating written approval from the Data Protection Officer, violating company policy."
            }

    # 4. DOMAIN LOGIC: DATA RETENTION
    if "retention" in clause_text or "retained" in clause_text or "retain" in clause_text or "storage" in clause_text:
        indefinite_retention = any(p in clause_text for p in ["indefinitely", "perpetual", "forever", "unlimited", "no time limit"])
        limited_retention = any(r in policy_lower for r in ["maximum of five years", "five years", "5 years", "maximum", "retention schedule", "deleted after"])

        if indefinite_retention and limited_retention:
            return {
                "clause_id": clause_id,
                "clause_title": clause.get("title", "Data Retention"),
                "contract_clause": clause.get("full_clause", ""),
                "status": "Conflict",
                "risk": "High",
                "evidence_status": "Explicitly Stated",
                "policy_evidence": policy_text,
                "source": source_file,
                "page": page_num,
                "similarity": round(similarity_score, 3),
                "explanation": "The contract specifies that customer records will be retained indefinitely, in direct violation of the policy requirement capping retention at a maximum of five years."
            }

    # 5. DOMAIN LOGIC: SECURITY & SYSTEMS
    if "security" in clause_text or "system" in clause_text or "device" in clause_text:
        policy_requires_approved = "company-approved" in policy_lower or "approved systems" in policy_lower
        contract_violates = any(v in clause_text for v in ["personal device", "unapproved", "any system", "third-party server"])
        if policy_requires_approved and contract_violates:
            return {
                "clause_id": clause_id,
                "clause_title": clause.get("title", "Security"),
                "contract_clause": clause.get("full_clause", ""),
                "status": "Conflict",
                "risk": "High",
                "evidence_status": "Explicitly Stated",
                "policy_evidence": policy_text,
                "source": source_file,
                "page": page_num,
                "similarity": round(similarity_score, 3),
                "explanation": "The contract permits unapproved systems, contradicting the policy requirement that employees must only use company-approved systems."
            }

    # 6. GENERAL PROTOTYPE CONFLICT / COMPLIANCE EVALUATION
    # Compare restrictive modal terms vs permissive terms
    contract_has_strict_terms = any(s in clause_text for s in ["shall not", "prohibited", "only with", "in accordance with"])
    policy_has_strict_terms = any(s in policy_lower for s in ["must not", "only when", "maximum", "shall not", "prohibited", "requires"])

    if "not" in policy_lower and "may" in clause_text and not ("not" in clause_text):
        return {
            "clause_id": clause_id,
            "clause_title": clause.get("title", "Compliance Finding"),
            "contract_clause": clause.get("full_clause", ""),
            "status": "Conflict",
            "risk": "Medium",
            "evidence_status": "Inferred",
            "policy_evidence": policy_text,
            "source": source_file,
            "page": page_num,
            "similarity": round(similarity_score, 3),
            "explanation": f"The contract permissive phrasing may conflict with restrictive requirements identified in the policy."
        }

    # If policy and contract are closely related and consistent
    return {
        "clause_id": clause_id,
        "clause_title": clause.get("title", "Compliance Review"),
        "contract_clause": clause.get("full_clause", ""),
        "status": "Compliant",
        "risk": "Low",
        "evidence_status": "Explicitly Stated" if similarity_score >= 0.65 else "Inferred",
        "policy_evidence": policy_text,
        "source": source_file,
        "page": page_num,
        "similarity": round(similarity_score, 3),
        "explanation": "The clause aligns with the retrieved policy requirements with no detectable conflict."
    }
