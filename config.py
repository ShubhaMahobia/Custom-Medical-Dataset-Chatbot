"""
Configuration settings for the Medical Chatbot
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

def get_secret(key, default=None):
    """
    Get secret from Streamlit secrets or environment variables
    Priority: Streamlit secrets > Environment variables > Default
    """
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and st.secrets:
            return st.secrets.get(key, default)
    except:
        pass
    
    # Fall back to environment variables
    return os.environ.get(key, default)

# API Keys
PINECONE_API_KEY = get_secret('PINECONE_API_KEY')
OPENAI_API_KEY = get_secret('OPENAI_API_KEY')

# Pinecone Settings
PINECONE_INDEX_NAME = "medical-knowledge-base"
PINECONE_DIMENSIONS = 384  # For sentence-transformers/all-MiniLM-L6-v2
PINECONE_METRIC = "cosine"

# Embedding Model Settings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Text Processing Settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 20

# LLM Settings
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1

# Retrieval Settings
RETRIEVER_K = 3  # Number of chunks to retrieve

# File Paths
PDF_DATA_PATH = "./"  # Directory containing PDF files

# UI Settings
PAGE_TITLE = "Medical Chatbot"
PAGE_ICON = "��"
LAYOUT = "wide" 