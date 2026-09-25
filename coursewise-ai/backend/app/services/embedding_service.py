import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Check for sentence_transformers availability
_HAS_SENTENCE_TRANSFORMERS = False
_st_model = None

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    _HAS_SENTENCE_TRANSFORMERS = False

# Scikit-learn fallback dense embedding generator
from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer


class EmbeddingService:
    """
    Lightweight local embedding service and vector index.
    Uses SentenceTransformers if available, otherwise generates
    fixed dense semantic embeddings using normalized HashingVectorizer
    with exact numpy cosine similarity vector search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", vector_dim: int = 128):
        self.model_name = model_name
        self.vector_dim = vector_dim
        self.use_st = _HAS_SENTENCE_TRANSFORMERS
        self._st_model = None
        self._hasher = HashingVectorizer(
            n_features=self.vector_dim,
            alternate_sign=False,
            stop_words="english",
            norm="l2"
        )

    def _get_st_model(self):
        global _st_model
        if not self.use_st:
            return None
        if _st_model is None:
            try:
                _st_model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer model {self.model_name}: {e}. Falling back to HashingVectorizer.")
                self.use_st = False
        return _st_model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings for a list of texts."""
        if not texts:
            return []

        # Try SentenceTransformers if available
        if self.use_st:
            try:
                model = self._get_st_model()
                if model:
                    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                    return embeddings.tolist()
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed: {e}. Using HashingVectorizer.")

        # Fixed-dimension normalized HashingVectorizer fallback
        valid_texts = [t.strip() if t.strip() else "content" for t in texts]
        sparse_vecs = self._hasher.transform(valid_texts)
        dense_vecs = sparse_vecs.toarray()
        
        # Ensure unit L2 normalization
        norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = dense_vecs / norms
        return normalized.tolist()

    @staticmethod
    def search_similar(
        query_vector: List[float],
        corpus_vectors: List[List[float]],
        top_k: int = 5
    ) -> List[int]:
        """
        Cosine similarity search over corpus vectors.
        Returns indices of top_k most similar vectors.
        """
        if not corpus_vectors or not query_vector:
            return []

        q = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm > 0:
            q = q / q_norm

        c = np.array(corpus_vectors, dtype=np.float32)
        c_norms = np.linalg.norm(c, axis=1, keepdims=True)
        c_norms[c_norms == 0] = 1.0
        c_normed = c / c_norms

        scores = np.dot(c_normed, q)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return top_indices.tolist()


# Global singleton instance
embedding_service = EmbeddingService()
