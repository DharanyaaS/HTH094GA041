from typing import List
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model_instance = None

def get_embedding_model() -> SentenceTransformer:
    """
    Lazy singleton loader for the sentence-transformers model.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer(MODEL_NAME)
    return _model_instance

def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for a single text string using all-MiniLM-L6-v2.
    """
    model = get_embedding_model()
    clean_text = text.strip() if text else ""
    embedding = model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings in batch.
    """
    if not texts:
        return []
    model = get_embedding_model()
    clean_texts = [t.strip() for t in texts]
    embeddings = model.encode(clean_texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()
