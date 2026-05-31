"""
Document creation and management utilities.
"""

import uuid
from typing import List
from langchain_core.documents import Document


def create_documents(
    texts: List[str],
    image_base64s: List[str],
    image_summaries: List[str],
    tables: List[str],
    table_summaries: List[str]
) -> List[Document]:
    """
    Create LangChain Document objects from extracted content.
    
    Each document contains:
    - page_content: Text used for similarity search (summary)
    - metadata: Type and original content for retrieval
    
    Args:
        texts (List[str]): List of text elements
        image_base64s (List[str]): List of base64-encoded images
        image_summaries (List[str]): List of image summaries
        tables (List[str]): List of table elements
        table_summaries (List[str]): List of table summaries
        
    Returns:
        List[Document]: List of LangChain Document objects
    """
    documents = []
    
    # Add text documents
    for content in texts:
        doc = Document(
            page_content=content,
            metadata={
                "id": str(uuid.uuid4()),
                "type": "text",
                "original_content": content
            }
        )
        documents.append(doc)
    
    # Add table summary documents
    for content, summary in zip(tables, table_summaries):
        doc = Document(
            page_content=summary,
            metadata={
                "id": str(uuid.uuid4()),
                "type": "table",
                "original_content": content
            }
        )
        documents.append(doc)
    
    # Add image summary documents
    for b64, summary in zip(image_base64s, image_summaries):
        doc = Document(
            page_content=summary,
            metadata={
                "id": str(uuid.uuid4()),
                "type": "image",
                "original_content": b64
            }
        )
        documents.append(doc)
    
    return documents


def prepare_context(reranked_docs: List[Document]) -> tuple:
    """
    Prepare context string and extract relevant images from reranked documents.
    
    Args:
        reranked_docs (List[Document]): Reranked documents from RAG
        
    Returns:
        tuple: (context_string, list_of_image_base64s)
    """
    context = ""
    relevant_images = []
    
    for doc in reranked_docs:
        doc_type = doc.metadata.get("type")
        original_content = doc.metadata.get("original_content")
        
        if doc_type == "text":
            context += original_content + "\n---\n"
        
        elif doc_type == "table":
            # Use page_content (LLM summary) not original_content (raw HTML)
            # Raw HTML tables are noisy — summary is what was embedded and retrieved
            context += doc.page_content + "\n---\n"
        
        elif doc_type == "image":
            context += doc.page_content + "\n---\n"
            relevant_images.append(original_content)
    
    return context, relevant_images