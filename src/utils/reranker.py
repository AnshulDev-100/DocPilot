"""
Cross-encoder based document reranking for improved retrieval.
"""

from typing import List
import streamlit as st
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from src.config import CROSS_ENCODER_MODEL, RERANK_TOP_N


@st.cache_resource
def load_cross_encoder():
    """
    Load and cache the cross-encoder model.
    Cached to avoid reloading on every Streamlit rerun.
    
    Returns:
        CrossEncoder: Loaded cross-encoder model
    """
    return CrossEncoder(CROSS_ENCODER_MODEL)


def rerank_documents(
    query: str,
    retrieved_docs: List[Document],
    top_n: int = RERANK_TOP_N
) -> List[Document]:
    """
    Rerank documents using cross-encoder for better relevance.
    
    Process:
    1. Load cross-encoder
    2. Score each (query, document) pair
    3. Sort by score descending
    4. Return top_n documents
    
    Args:
        query (str): User's search query
        retrieved_docs (List[Document]): Documents from vector similarity search
        top_n (int): Number of top documents to return
        
    Returns:
        List[Document]: Reranked documents sorted by relevance
    """
    if not retrieved_docs:
        return []
    
    cross_encoder = load_cross_encoder()
    
    # Create (query, document) pairs
    pairs = [(query, doc.page_content) for doc in retrieved_docs]
    
    # Score all pairs
    scores = cross_encoder.predict(pairs)
    
    # Zip scores with documents
    scored_docs = list(zip(scores, retrieved_docs))
    
    # Sort by score (descending)
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    # Return only documents, not scores
    return [doc for score, doc in scored_docs[:top_n]]