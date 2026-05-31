"""
Prompt templates for DocPilot application.
"""

from langchain_core.prompts import ChatPromptTemplate
from src.config import SUMMARIZATION_PROMPT, RAG_RESPONSE_PROMPT, IMAGE_SUMMARY_PROMPT


def get_summarization_chain(llm):
    """
    Create a chain for summarizing PDF elements.
    
    Args:
        llm: LangChain LLM instance
        
    Returns:
        Chain: Summarization chain
    """
    from langchain_core.output_parsers import StrOutputParser
    
    prompt = ChatPromptTemplate.from_template(SUMMARIZATION_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return chain


def get_rag_chain(llm):
    """
    Create a chain for RAG-based question answering.
    
    Args:
        llm: LangChain LLM instance
        
    Returns:
        Chain: RAG chain
    """
    from langchain_core.output_parsers import StrOutputParser
    
    prompt = ChatPromptTemplate.from_template(RAG_RESPONSE_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return chain


def get_image_summary_prompt() -> str:
    """
    Get the prompt for image summarization.
    
    Returns:
        str: Image summary prompt
    """
    return IMAGE_SUMMARY_PROMPT