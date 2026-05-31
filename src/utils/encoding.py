"""
Image encoding utilities for multimodal RAG.
"""

import base64
from typing import Tuple


def encode_image(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64-encoded image string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def decode_image(base64_string: str) -> bytes:
    """
    Decode a base64 string back to image bytes.
    
    Args:
        base64_string (str): Base64-encoded image string
        
    Returns:
        bytes: Decoded image bytes
    """
    return base64.b64decode(base64_string)


def create_image_message(base64_image: str, prompt: str) -> dict:
    """
    Create a structured message for vision LLM with image and text.
    
    Args:
        base64_image (str): Base64-encoded image
        prompt (str): Text prompt to send with the image
        
    Returns:
        dict: Structured message for LangChain HumanMessage
    """
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
        }
    }