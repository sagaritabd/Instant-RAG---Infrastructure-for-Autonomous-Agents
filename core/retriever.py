from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

def chunk_text(t: str, n: int = 300) -> List[str]:
    """
    Split text into chunks of size n.
    
    Args:
        t: Text to chunk
        n: Chunk size in characters
        
    Returns:
        List of text chunks
    """
    if not t:
        return []
    return [t[i:i+n] for i in range(0, len(t), n)]

class SimpleRetriever:
    """
    Simple semantic retriever using sentence transformers and cross-encoder reranking.
    """
    
    def __init__(self):
        self.docs: List[str] = []
        self.meta: List[Dict[str, Any]] = []
        
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            logger.info("Retriever models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading retriever models: {e}")
            raise

    def add_documents(self, chunks: List[str], source_name: str):
        """
        Add document chunks to the retriever.
        
        Args:
            chunks: List of text chunks to add
            source_name: Source filename or identifier
        """
        try:
            for c in chunks:
                if c.strip():  # Only add non-empty chunks
                    self.docs.append(c)
                    self.meta.append({"source": source_name})
            logger.info(f"Added {len(chunks)} chunks from {source_name}")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(self, q: str, top_k: int = 5) -> Tuple[List[str], List[Dict], List[float]]:
        """
        Search for relevant documents using semantic similarity and reranking.
        
        Args:
            q: Query text
            top_k: Number of results to return
            
        Returns:
            Tuple of (candidate texts, citations, reranker scores)
        """
        if not self.docs:
            logger.warning("No documents available for search")
            return [], [], []
        
        if not q.strip():
            logger.warning("Empty query provided")
            return [], [], []
        
        try:
            # Encode query
            qv = self.model.encode([q])[0]
            
            # Encode all documents
            dv = self.model.encode(self.docs)
            
            # Compute similarities
            sims = np.dot(dv, qv)
            
            # Get top-k candidates
            top_k = min(top_k, len(self.docs))
            idx = sims.argsort()[-top_k:][::-1]
            
            cands = [self.docs[i] for i in idx]
            
            # Rerank candidates
            pairs = [[q, c] for c in cands]
            scores = self.reranker.predict(pairs)
            
            # Get citations
            cites = [self.meta[i] for i in idx]
            
            logger.info(f"Search completed: {len(cands)} results")
            return cands, cites, list(scores)
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return [], [], []

def weave_answer(results: List[str], cites: List[Dict]) -> Dict[str, Any]:
    """
    Combine search results into a formatted answer.
    
    Args:
        results: List of result texts
        cites: List of citation metadata
        
    Returns:
        Dictionary with answer and citations
    """
    if not results:
        return {
            "answer": "No relevant information found.",
            "citations": []
        }
    
    return {
        "answer": "\n\n".join(results),
        "citations": cites
    }
