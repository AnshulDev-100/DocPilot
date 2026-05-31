"""
Configuration and constants for DocPilot application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==== API Keys & Credentials ====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# ==== LLM Configuration ====
LLM_MODEL = "gpt-4o"
VISION_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.1

# ==== PDF Processing ====
PDF_EXTRACTION_STRATEGY = "hi_res"  # High resolution extraction
IMAGE_OUTPUT_DIR = "./raw_elements"
UPLOAD_DIR = "./uploads"

# ==== Vector Store ====
FAISS_DIMENSION = 1536  # OpenAI embeddings dimension
SIMILARITY_SEARCH_K = 10  # Number of documents to retrieve

# ==== Reranking ====
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-TinyBERT-L-2-v2"
RERANK_TOP_N = 5

# ==== Batch Processing ====
SUMMARIZATION_MAX_CONCURRENCY = 5

# ==== UI Text ====
APP_TITLE = "DocPilot: The MultiModal RAG Assistant"
APP_DESCRIPTION = "Upload a PDF to ask questions about its content."

# ==== Prompts ====
SUMMARIZATION_PROMPT = """You are an assistant tasked with summarizing text for retrieval. \
Give a concise summary of the following content that is well optimized for retrieval:
---
{element}"""

IMAGE_SUMMARY_PROMPT = "Summarize this image for retrieval. Describe its key elements and purpose concisely."

RAG_RESPONSE_PROMPT = """You are an expert AI assistant. Answer the question based ONLY on the following context, \
which can include text, tables, and image summaries:

CONTEXT:
{context}

QUESTION: {question}

If the context does not contain the answer, say "Sorry, I don't have enough information to answer that."

Answer:"""

# ==== Logging ====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")