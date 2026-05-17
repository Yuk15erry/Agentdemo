"""
RAG Engine — Retrieval-Augmented Generation for product knowledge.
Uses FAISS for vector search with sentence-transformer embeddings.
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_VECTOR_DEPS = True
except ImportError:
    HAS_VECTOR_DEPS = False

from config.settings import RAG_INDEX_PATH, EMBEDDING_MODEL, RAG_TOP_K
from utils.logger import get_logger

logger = get_logger("RAGEngine")


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for product FAQ and knowledge base.
    
    Supports:
    - Document indexing with embeddings
    - Semantic search
    - Multilingual retrieval
    """
    
    def __init__(self, index_path: str = None):
        self.index_path = index_path or RAG_INDEX_PATH
        self.documents: List[Dict] = []
        self.index = None
        self.embedder = None
        
        if HAS_VECTOR_DEPS:
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            logger.info(f"RAG Engine initialized with model: {EMBEDDING_MODEL}")
        else:
            logger.warning("Vector dependencies not installed. Using keyword search fallback.")
    
    def load_documents(self, documents: List[Dict]):
        """Load documents into the RAG engine."""
        self.documents = documents
        logger.info(f"Loaded {len(documents)} documents")
    
    def build_index(self):
        """Build FAISS index from loaded documents."""
        if not HAS_VECTOR_DEPS or not self.documents:
            logger.warning("Cannot build index: missing dependencies or no documents")
            return
        
        texts = [doc.get("content", "") for doc in self.documents]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else ".", exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        
        logger.info(f"FAISS index built with {len(self.documents)} documents, dimension={dimension}")
    
    async def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for relevant documents."""
        top_k = top_k or RAG_TOP_K
        
        if self.index is not None and HAS_VECTOR_DEPS:
            return self._vector_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict]:
        """Semantic search using FAISS."""
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), top_k
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = dict(self.documents[idx])
                doc["relevance"] = float(1.0 / (1.0 + distances[0][i]))
                results.append(doc)
        
        return results
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Fallback keyword-based search."""
        query_lower = query.lower()
        scored = []
        
        for doc in self.documents:
            content = doc.get("content", "").lower()
            # Simple TF-like scoring
            score = sum(1 for word in query_lower.split() if word in content)
            if score > 0:
                scored.append({**doc, "relevance": score / len(query_lower.split())})
        
        scored.sort(key=lambda x: x["relevance"], reverse=True)
        return scored[:top_k]
    
    def get_stats(self) -> Dict:
        """Get RAG engine statistics."""
        return {
            "documents_indexed": len(self.documents),
            "has_vector_index": self.index is not None,
            "embedding_model": EMBEDDING_MODEL if HAS_VECTOR_DEPS else "keyword_fallback",
            "index_path": str(self.index_path)
        }
