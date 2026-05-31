"""
Vector store creation and management using FAISS.
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from src.config import SIMILARITY_SEARCH_K


def create_vector_store(documents: List[Document]) -> FAISS:
    """
    Create FAISS vector store from documents.
    
    Process:
    1. Initialize OpenAI embeddings (1536 dimensions)
    2. Embed all documents
    3. Store in FAISS index
    
    Args:
        documents (List[Document]): List of LangChain documents
        
    Returns:
        FAISS: Vector store for similarity search
    """
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )
    return vectorstore


def similarity_search(
    vector_store: FAISS,
    query: str,
    k: int = SIMILARITY_SEARCH_K
) -> List[Document]:
    """
    Retrieve documents similar to the query.
    
    Args:
        vector_store (FAISS): FAISS vector store
        query (str): Search query
        k (int): Number of documents to retrieve
        
    Returns:
        List[Document]: Retrieved documents
    """
    return vector_store.similarity_search(query, k=k)