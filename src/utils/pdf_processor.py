"""
PDF processing and element extraction utilities.
"""

import os
import platform
from typing import List, Tuple
from unstructured.partition.pdf import partition_pdf
import streamlit as st

# Windows: set tesseract path directly on unstructured_pytesseract module
# os.environ approach does NOT work — must set the attribute directly
if platform.system() == "Windows":
    try:
        import unstructured_pytesseract
        tesseract_path = os.getenv(
            "TESSERACT_CMD",
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        unstructured_pytesseract.pytesseract.tesseract_cmd = tesseract_path
    except ImportError:
        pass


def extract_pdf_elements(file_path: str, image_output_dir: str) -> Tuple[List[str], List[str]]:
    """
    Extract text and table elements from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        image_output_dir (str): Directory to save extracted images
        
    Returns:
        Tuple[List[str], List[str]]: Lists of text and table contents
    """
    # Ensure output directory exists
    os.makedirs(image_output_dir, exist_ok=True)
    
    # Partition PDF with high resolution strategy
    raw_elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_output_dir=image_output_dir
    )
    
    # Use type(element).__name__ — returns bare class name e.g. "NarrativeText"
    # str(type(element)) returns "<class '...NarrativeText'>" — set lookup never matches
    TEXT_NAMES = {"Text", "NarrativeText", "ListItem", "FigureCaption", "Title"}

    texts = []
    tables = []

    for element in raw_elements:
        element_name = type(element).__name__

        if element_name in TEXT_NAMES:
            texts.append(str(element))
        elif element_name == "Table":
            tables.append(str(element))
    
    return texts, tables


def get_extracted_images(image_output_dir: str) -> List[str]:
    """
    Get list of extracted image file paths.
    
    Args:
        image_output_dir (str): Directory containing extracted images
        
    Returns:
        List[str]: Sorted list of image file paths
    """
    if not os.path.exists(image_output_dir):
        return []
    
    image_paths = [
        os.path.join(image_output_dir, f)
        for f in os.listdir(image_output_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    
    return sorted(image_paths)


def save_uploaded_file(uploaded_file, temp_dir: str) -> str:
    """
    Save an uploaded file to temporary directory.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        temp_dir (str): Temporary directory path
        
    Returns:
        str: Full path to saved file
    """
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path