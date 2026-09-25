import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

# Vector store directory in C:/Compliance-AI/backend/vector_store
VECTOR_STORE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "vector_store")
)
COLLECTION_NAME = "compliance_policies"

_client_instance = None
_collection_instance = None

def get_chroma_client() -> chromadb.PersistentClient:
    global _client_instance
    if _client_instance is None:
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        _client_instance = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    return _client_instance

def get_policy_collection():
    global _collection_instance
    client = get_chroma_client()
    # Using cosine distance metric for accurate normalized similarity
    _collection_instance = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return _collection_instance

def delete_source_documents(source_name: str) -> None:
    """
    Remove any existing chunks for a specific source document to prevent duplicates.
    """
    collection = get_policy_collection()
    try:
        collection.delete(where={"source": source_name})
    except Exception:
        pass

def add_policy_chunks(chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
    """
    Store policy chunks with metadata into ChromaDB.
    """
    if not chunks:
        return 0

    collection = get_policy_collection()
    
    # First, clear any prior chunks with the same source
    sources_to_clear = {c["source"] for c in chunks}
    for src in sources_to_clear:
        delete_source_documents(src)

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "page": int(c["page"]),
            "source": str(c["source"]),
            "title": str(c.get("title", ""))
        }
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)

def query_policy_store(query_embedding: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Query ChromaDB for most relevant policy chunks.
    Calculates cosine similarity = 1.0 - distance.
    """
    collection = get_policy_collection()
    total_docs = collection.count()
    if total_docs == 0:
        return []

    actual_k = min(n_results, total_docs)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_k,
        include=["documents", "metadatas", "distances"]
    )

    formatted_results: List[Dict[str, Any]] = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results else []
        dists = results["distances"][0] if "distances" in results else []
        ids = results["ids"][0] if "ids" in results else []

        for i in range(len(docs)):
            dist = dists[i] if i < len(dists) else 1.0
            # With cosine space, similarity = 1 - distance
            similarity = max(0.0, min(1.0, 1.0 - float(dist)))
            meta = metas[i] if i < len(metas) else {}
            
            formatted_results.append({
                "chunk_id": ids[i] if i < len(ids) else f"chunk_{i}",
                "text": docs[i],
                "page": meta.get("page", 1),
                "source": meta.get("source", "Unknown"),
                "title": meta.get("title", ""),
                "distance": float(dist),
                "similarity": similarity
            })

    # Sort descending by similarity
    formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
    return formatted_results

def count_chunks() -> int:
    collection = get_policy_collection()
    return collection.count()

def get_indexed_sources() -> List[Dict[str, Any]]:
    """
    Returns unique policy sources and their chunk count.
    """
    collection = get_policy_collection()
    data = collection.get(include=["metadatas"])
    sources_summary: Dict[str, Dict[str, Any]] = {}

    if data and "metadatas" in data and data["metadatas"]:
        for m in data["metadatas"]:
            if not m:
                continue
            src = m.get("source", "Unknown")
            page = m.get("page", 1)
            if src not in sources_summary:
                sources_summary[src] = {
                    "source": src,
                    "chunks": 0,
                    "max_page": 1
                }
            sources_summary[src]["chunks"] += 1
            if page > sources_summary[src]["max_page"]:
                sources_summary[src]["max_page"] = page

    return list(sources_summary.values())

def reset_policy_store() -> None:
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    global _collection_instance
    _collection_instance = None
