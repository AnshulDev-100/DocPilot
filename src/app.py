"""
DocPilot: Multimodal RAG Assistant
Main Streamlit application file.
"""

import sys
import os
# Add project root to path so 'src.*' imports resolve regardless of how streamlit is invoked
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Import modular components
from src.config import (
    APP_TITLE, APP_DESCRIPTION,
    LLM_MODEL, VISION_MODEL, LLM_TEMPERATURE,
    UPLOAD_DIR, IMAGE_OUTPUT_DIR
)
from src.utils.pdf_processor import extract_pdf_elements, get_extracted_images, save_uploaded_file
from src.utils.document_handler import create_documents, prepare_context
from src.utils.vector_store import create_vector_store, similarity_search
from src.utils.reranker import rerank_documents
from src.utils.encoding import encode_image
from src.prompts.templates import get_summarization_chain, get_rag_chain, get_image_summary_prompt


# ==== Page Configuration ====
st.set_page_config(page_title="DocPilot", layout="wide")
st.title(APP_TITLE)
st.write(APP_DESCRIPTION)


# ==== Core Pipeline Function ====
def process_uploaded_file(uploaded_file, llm, vision_llm):
    """
    Process uploaded PDF file through the multimodal RAG pipeline.

    Steps:
    1. Save uploaded file to disk
    2. Extract text, tables, and images from PDF
    3. Summarize tables using LLM
    4. Summarize images using vision LLM
    5. Create LangChain documents and build FAISS vector store
    6. Store vector store in Streamlit session state
    """
    # Save uploaded file to temp directory
    file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)

    # ---- Step 1: Extract PDF Elements ----
    with st.spinner("Step 1/4: Extracting elements from the PDF..."):
        texts, tables = extract_pdf_elements(file_path, IMAGE_OUTPUT_DIR)

    # ---- Step 2: Summarize Tables ----
    summarize_chain = get_summarization_chain(llm)

    with st.spinner("Step 2/4: Summarizing text and tables..."):
        table_summaries = (
            summarize_chain.batch(tables, {"max_concurrency": 5})
            if tables else []
        )

    # ---- Step 3: Summarize Images via Vision LLM ----
    with st.spinner("Step 3/4: Summarizing images..."):
        image_base64s = []
        image_summaries = []
        image_paths = get_extracted_images(IMAGE_OUTPUT_DIR)

        for img_path in image_paths:
            b64 = encode_image(img_path)
            image_base64s.append(b64)

            image_message = HumanMessage(
                content=[
                    {"type": "text", "text": get_image_summary_prompt()},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    }
                ]
            )
            summary = vision_llm.invoke([image_message]).content
            image_summaries.append(summary)

    # ---- Step 4: Build Vector Store ----
    with st.spinner("Step 4/4: Creating vector store..."):
        documents = create_documents(
            texts, image_base64s, image_summaries,
            tables, table_summaries
        )
        vectorstore = create_vector_store(documents)

    # Persist vector store in session state
    st.session_state.db = vectorstore
    st.success("✅ File processed successfully! You can now ask questions.")


# ==== Sidebar: File Upload ====
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file:
        if st.button("Process Document", use_container_width=True):
            llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
            vision_llm = ChatOpenAI(model=VISION_MODEL, temperature=LLM_TEMPERATURE)
            process_uploaded_file(uploaded_file, llm, vision_llm)


# ==== Chat Interface ====
# Initialize message history on first run
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("images"):
            for img_b64 in message["images"]:
                st.image(base64.b64decode(img_b64), width=300)

# New chat input
prompt = st.chat_input("Ask a question about the document...")

if prompt and prompt.strip():
    # Guard: document must be processed first
    if "db" not in st.session_state or st.session_state.db is None:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        # ---- Display User Message ----
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # ---- Generate & Display Assistant Response ----
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # 1. Broad similarity search (k=10)
                retrieved_docs = similarity_search(st.session_state.db, prompt)

                # 2. Narrow down via cross-encoder reranking (top 5)
                reranked_docs = rerank_documents(prompt, retrieved_docs)

                # 3. Build context string + pull relevant images
                context, relevant_images = prepare_context(reranked_docs)

                # 4. Run RAG chain
                llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
                response = get_rag_chain(llm).invoke(
                    {"context": context, "question": prompt}
                )

                # 5. Render response
                st.markdown(response)

                if relevant_images:
                    st.write("**Relevant images from the document:**")
                    for img_b64 in relevant_images:
                        st.image(base64.b64decode(img_b64), width=300)

        # Persist assistant message with any images
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "images": relevant_images if relevant_images else []
        })